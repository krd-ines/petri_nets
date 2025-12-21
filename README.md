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


# Project Structure
---
## 1. "net" folder
This folder contains files related to the creation of the petri net.
It includes the files:
* **create.py**: contains methods to build a petri net using SNAKES library

## 2. "tree" folder
This folder contains files relative to the logic of building the coverability tree (arbre de couverture)
It includes the files:
* **algo.py**: contains the main tree construction logic and steps (karp and miller's algorithm implementation)
* **export.py**: contains methods to covert the resulting tree to ```.dot``` and image formats
* **markings.py**: contains methods to compare markings and to handle their changes inclding accelerations using omega (couverture)
* **matrices.py**: helps in extracting the ```pre``` and ```post``` matrices from a SNAKES petri net
* **print.py**: contains methods to diplay the algorithm's result on the terminal
* **transitions.py**: has methods about transitions like checking if one is enabled (franchissable) and firing one (franchir)

## 3. "viz" folder
This folder is currently just a test file that was used to test using GraphViz library

## 4. main.py
This is the main part of the project, it contains the construction of a petri net, applying the algorithm on it, printing the result and generating an image of the result
