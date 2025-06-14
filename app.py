import streamlit as st
from itertools import combinations_with_replacement
import re
from typing import List, Tuple, Iterator, Dict, Any, Optional, Union
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Professional Resistor Calculator",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State ---
if 'results_calculated' not in st.session_state:
    st.session_state.results_calculated = False
if 'series_results' not in st.session_state:
    st.session_state.series_results = []
if 'parallel_results' not in st.session_state:
    st.session_state.parallel_results = []
if 'num_to_display' not in st.session_state:
    st.session_state.num_to_display = 5

# --- Constants ---
E12_VALUES = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
STANDARD_RESISTORS = sorted([j * 10**i for i in range(7) for j in E12_VALUES])
MAX_RESISTORS_IN_COMBO = 4
RESULTS_INCREMENT = 5

# --- Helper Functions ---

def parse_resistance(value: str) -> Optional[float]:
    if not value: return None
    pattern = r"^\s*(\d*\.?\d+)\s*([kmg])?\s*$"
    match = re.match(pattern, value.strip(), re.IGNORECASE)
    if not match: return None
    number_str, prefix = match.groups()
    number = float(number_str)
    PREFIXES = {"k": 10**3, "m": 10**6, "g": 10**9}
    multiplier = PREFIXES.get(prefix.lower() if prefix else "", 1)
    return number * multiplier

def format_resistance(value: float) -> str:
    if value >= 1_000_000: return f"{value / 1_000_000:.2f}".replace(".00", "") + " MΩ"
    if value >= 1_000: return f"{value / 1_000:.2f}".replace(".00", "") + " kΩ"
    return f"{int(value)} Ω"

def get_resistor_colors(value: float) -> List[str]:
    COLOR_CODES = {0: 'black', 1: 'brown', 2: 'red', 3: 'orange', 4: 'yellow', 5: 'green', 6: 'blue', 7: 'purple', 8: 'gray', 9: 'white'}
    if value == 0: return ['black', 'black', 'black']
    try:
        s_val = f"{value:.9E}"
        parts = s_val.split('E')
        mantissa_str, exponent = parts[0].replace('.', ''), int(parts[1])
        d1, d2 = int(mantissa_str[0]), int(mantissa_str[1])
        num_zeros = exponent - 1
        return [COLOR_CODES.get(d, 'black') for d in [d1, d2, num_zeros]]
    except (IndexError, ValueError): return ['black', 'black', 'black']

def color_bands_html(colors: List[str]) -> str:
    return "".join(f'<div style="background-color:{c}; width:15px; height:40px; display:inline-block; border:1.5px solid #333; margin-right:2px; border-radius: 4px; vertical-align: middle;"></div>' for c in colors)

def calculate_combination_value(resistors: Tuple[float], mode: str) -> float:
    if not resistors: return 0
    if mode == 'series': return sum(resistors)
    if mode == 'parallel':
        if any(r == 0 for r in resistors): return 0
        return 1 / sum(1 / r for r in resistors)
    return 0

def find_combinations(target: float, tolerance: float, mode: str, num_resistors_option: Union[int, str]) -> Iterator[Tuple[float, ...]]:
    search_space = [r for r in STANDARD_RESISTORS if r <= target * (1 + tolerance)] if mode == 'series' else STANDARD_RESISTORS
    
    if num_resistors_option == "Automatic":
        count_range = range(1, MAX_RESISTORS_IN_COMBO + 1)
    else:
        count_range = range(int(num_resistors_option), int(num_resistors_option) + 1)

    for i in count_range:
        for combo in combinations_with_replacement(search_space, i):
            total_resistance = calculate_combination_value(combo, mode)
            if target > 0 and abs(total_resistance - target) / target <= tolerance:
                yield combo

def generate_circuit_dot(combo: Tuple[float, ...], mode: str, is_best: bool) -> str:
    border_color = "#00b4d8" if is_best else "#adb5bd"
    node_color = "#ade8f4" if is_best else "#dee2e6"
    dot_lines = ['digraph G {', '    rankdir=LR;', '    bgcolor="transparent";', f'    node [shape=box, style="filled", fillcolor="{node_color}", fontcolor="black", color="{border_color}", penwidth=1.5];', f'    edge [color="{border_color}"];']
    resistor_labels = {f'R{i+1}': format_resistance(val) for i, val in enumerate(combo)}
    if mode == 'series':
        path = " -> ".join(resistor_labels.keys())
        dot_lines.append(f'    "In" [fontcolor="#333", style=plaintext]; "Out" [fontcolor="#333", style=plaintext]; "In" -> {path} -> "Out";')
    elif mode == 'parallel':
        dot_lines.append('    In [shape=point, label=""]; Out [shape=point, label=""];')
        for r_name in resistor_labels.keys(): dot_lines.append(f'    In -> {r_name} -> Out;')
    for r_name, r_label in resistor_labels.items(): dot_lines.append(f'    {r_name} [label="{r_label}"];')
    dot_lines.append('}')
    return "\n".join(dot_lines)

def display_results_cards(results: List[Dict], mode: str):
    if not results:
        st.info(f"No suitable {mode} combinations were found.")
        return

    for i, res in enumerate(results[:st.session_state.num_to_display]):
        is_best = (i == 0)
        with st.container(border=True):
            if is_best:
                st.markdown("🏆 **Best Match**")
            
            op_symbol = " + " if mode == 'series' else " || "
            summary = op_symbol.join([format_resistance(r) for r in sorted(list(res['combo']))])
            st.markdown(f"#### {summary}")

            main_cols = st.columns([2, 3])
            with main_cols[0]:
                st.graphviz_chart(generate_circuit_dot(res['combo'], mode, is_best), use_container_width=True)
            
            with main_cols[1]:
                metric_cols = st.columns(2)
                metric_cols[0].metric("Resulting Value", format_resistance(res['value']))
                metric_cols[1].metric("Error", f"{res['error']:.3f}%")
                
                st.markdown("**Component Breakdown:**")
                for r_val in sorted(list(res['combo'])):
                    comp_cols = st.columns([2, 1])
                    with comp_cols[0]:
                        st.markdown(f"<p style='font-size: 1.1em; text-align: left; margin-top: 10px;'>{format_resistance(r_val)}</p>", unsafe_allow_html=True)
                    with comp_cols[1]:
                        st.markdown(f"<div style='text-align: right;'>{color_bands_html(get_resistor_colors(r_val))}</div>", unsafe_allow_html=True)
                    st.divider()

    if len(results) > st.session_state.num_to_display:
        if st.button(f"Show More ({mode.title()})", key=f"more_{mode}", use_container_width=True):
            st.session_state.num_to_display += RESULTS_INCREMENT
            st.rerun()

# --- UI Layout ---

with st.sidebar:
    st.title("About & Settings")
    st.info("""
        **Professional Resistor Calculator v6.1**
        
        Developed by **Amin Fallah** & **Roham Shahmoradi**.
    """)
    st.number_input(
        'Initial results to show:',
        min_value=3, max_value=50, value=5, step=1,
        key='num_to_display_setting',
    )
    st.write("---")
    st.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

st.title("🛠️ Professional Resistor Calculator")
st.markdown("Find precise resistor combinations with advanced controls and visualizations.")

with st.container(border=True):
    st.subheader("1. Input Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_str = st.text_input('Target Resistance (e.g., 4.7k):', "10k")
    with col2:
        tolerance_percent = st.slider('Allowed Tolerance (%):', 0.1, 20.0, 1.0, 0.1)
    with col3:
        num_resistors_option = st.selectbox(
            'Number of Resistors:',
            options=["Automatic", 1, 2, 3, 4],
            index=0,
            help="Select the number of resistors to combine. 'Automatic' finds the best result using 1 to 4 resistors."
        )

    if st.button('Find Combinations', type="primary", use_container_width=True):
        target_val = parse_resistance(target_str)
        if target_val is None:
            st.error("Invalid resistance format. Please use formats like '10k', '4.7M', or '330'.")
            st.session_state.results_calculated = False
        elif target_val <= 0:
            st.error("Please enter a resistance value greater than zero.")
            st.session_state.results_calculated = False
        else:
            with st.spinner("Calculating all possible combinations..."):
                tolerance = tolerance_percent / 100
                
                def process_results(combos: List, mode: str) -> List[Dict[str, Any]]:
                    results = []
                    for combo in set(combos):
                        val = calculate_combination_value(combo, mode)
                        error = abs(val - target_val) / target_val * 100
                        results.append({"combo": combo, "value": val, "error": error})
                    return sorted(results, key=lambda x: (x['error'], len(x['combo'])))

                st.session_state.series_results = process_results(list(find_combinations(target_val, tolerance, 'series', num_resistors_option)), 'series')
                st.session_state.parallel_results = process_results(list(find_combinations(target_val, tolerance, 'parallel', num_resistors_option)), 'parallel')
                st.session_state.num_to_display = st.session_state.num_to_display_setting
                st.session_state.results_calculated = True

# --- Results Section ---
if st.session_state.results_calculated:
    st.header("2. Calculation Results", divider='rainbow')

    min_error_series = st.session_state.series_results[0]['error'] if st.session_state.series_results else float('inf')
    min_error_parallel = st.session_state.parallel_results[0]['error'] if st.session_state.parallel_results else float('inf')
    
    # --- NEW: Modern Summary Scorecard ---
    st.markdown("##### Results Summary")

    # Determine the winner
    winner_message = ""
    if min_error_series != float('inf') or min_error_parallel != float('inf'):
        if min_error_series < min_error_parallel:
            winner_message = "🏆 **Series Mode is More Accurate** for this target."
        elif min_error_parallel < min_error_series:
            winner_message = "🏆 **Parallel Mode is More Accurate** for this target."
        else:
            winner_message = "TIE: Both modes achieved the same top accuracy."
    
    if winner_message:
        st.success(winner_message, icon="✅")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            if winner_message and "Series" in winner_message:
                st.markdown("🏅 **Winner**")
            st.metric("Best Series Error", f"{min_error_series:.3f}%" if min_error_series != float('inf') else "N/A")

    with col2:
        with st.container(border=True):
            if winner_message and "Parallel" in winner_message:
                st.markdown("🏅 **Winner**")
            st.metric("Best Parallel Error", f"{min_error_parallel:.3f}%" if min_error_parallel != float('inf') else "N/A")
    
    st.divider()

    # --- Revert to st.tabs for result display ---
    tab_series, tab_parallel = st.tabs([f"**Series ({len(st.session_state.series_results)} combinations)**", f"**Parallel ({len(st.session_state.parallel_results)} combinations)**"])

    with tab_series:
        display_results_cards(st.session_state.series_results, 'series')
    
    with tab_parallel:
        display_results_cards(st.session_state.parallel_results, 'parallel')

else:
    st.info("Enter your target parameters and click 'Find Combinations' to start.")