# Petri Net Project Setup

This project uses the **SNAKES** library and **Graphviz** for Petri net modeling and visualization. Follow these steps to set up your environment on Windows.

---

## 1. Virtual Environment Management
```powershell
# Deactivate if you see (.venv) in your prompt
deactivate

# Force delete the old folder
rmdir /S /Q .venv

# Recreate using the main Python installation
python -m venv .venv
```

## 2. Activation and Verification
You must activate the environment every time you open a new terminal.
For Command Prompt (CMD):
```powershell
.\.venv\Scripts\activate.bat
```

## 3. Installation of Libraries
Install the necessary Python packages within your active virtual environment:
```poweshell

python -m pip install SNAKES
python -m pip install graphviz
```

## 4. System Dependency: Graphviz
The Python graphviz library is just a wrapper. You must also install the Graphviz software on your Windows system:

Download: Graphviz Windows Installer

Install: Run the .exe installer.

CRITICAL STEP: During installation, select the option:

"Add Graphviz to the system PATH for all users"

Restart VS Code: After installation, close and reopen VS Code to ensure the system recognizes the new PATH.

## 5. Running the Project
Once everything is configured, run the main script:
```powershell
python main.py
```
