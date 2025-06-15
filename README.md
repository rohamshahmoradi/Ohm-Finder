# Ohm Finder 🛠️

## 🚀 Live Demo

You can test this application live on **Hugging Face Spaces** by clicking the link below:

**[👉 Click here to try Ohm Finder](https://huggingface.co/spaces/rohamshahmoradi/Ohm-Finder)**

---

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An advanced web application for electronics engineers, students, and hobbyists to find the best series and parallel combinations of standard E12 series resistors to achieve a desired target resistance. This tool performs the necessary calculations and visualizes the results with circuit diagrams and resistor color codes.

---

### ✨ Key Features

-   **Series & Parallel Calculations**: Simultaneously finds the best combinations for both series and parallel configurations.
-   **Flexible Input**: Enter your target resistance using standard prefixes (e.g., `10k`, `4.7M`, `330`).
-   **Precise Controls**: Adjust the allowed tolerance and the number of resistors to use in the combination.
-   **Smart Results Display**: Highlights the best match with the lowest error, shows the exact error percentage, and compares the accuracy of series vs. parallel modes.
-   **Graphical Visualization**:
    -   **Circuit Diagrams**: Automatically generates a schematic diagram for each resulting combination.
    -   **Resistor Color Codes**: Displays the standard color bands for each individual resistor.
-   **Modern & Interactive UI**: Built with Streamlit for a smooth and user-friendly experience.

---


### ⚙️ Technologies Used

-   **Python**: The core programming language.
-   **Streamlit**: For building the interactive web application.
-   **Graphviz**: For generating and displaying the circuit diagrams.

---

### 👨‍💻 Running the Project Locally

If you want to run this project on your own machine, follow the steps below:

**1. Clone the Repository**

```bash
git clone [https://github.com/rohamshahmoradi/Ohm-Finder.git](https://github.com/rohamshahmoradi/Ohm-Finder.git)
cd Ohm-Finder
```
> **Note**: Replace the URL with your own repository's URL if it's different.

**2. Install Python Packages**

It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install the required packages
pip install -r requirements.txt
```

**3. Run the Application**

The application will open in your default web browser.

```bash
streamlit run app.py
```
> **Diagrams Note**: To ensure the circuit diagrams are displayed correctly, you may need to install [Graphviz](https://graphviz.org/download/) on your system.

---

### ✍️ Authors

This project was developed by **Amin Fallah** and **Roham Shahmoradi**.

---

### 📜 License

This project is licensed under the MIT License.
