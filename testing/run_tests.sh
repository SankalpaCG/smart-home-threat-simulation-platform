#!/bin/bash

# ==============================================================================
# SMART HOME THREAT SIMULATION PLATFORM - AUTOMATED VALIDATION SUITE
# ==============================================================================
# This script executes the academic validation and graph generation sequence.
# It ensures all Python dependencies are installed and runs the validators.
# ==============================================================================

echo "[*] Initializing Master's Level Testing & Validation Suite..."

# 1. Activate the virtual environment if it exists
if [ -f "../venv/bin/activate" ]; then
    echo "[*] Activating Python Virtual Environment..."
    source ../venv/bin/activate
else
    echo "[!] Virtual environment not found. Using system Python."
fi

# 2. Ensure mathematical graphing dependencies are installed
echo "[*] Verifying graphing dependencies (matplotlib, seaborn, pandas, scikit-learn)..."
pip install -q seaborn matplotlib pandas scikit-learn

# 3. Create the graphs directory if it was deleted
mkdir -p graphs

# 4. Run Dataset Validation
echo ""
echo "[*] --------------------------------------------------"
echo "[*] PHASE 1: Executing Mathematical Dataset Validation"
echo "[*] --------------------------------------------------"
python3 dataset_validator.py
echo "[+] Validation report saved to: testing/DATASET_VALIDATION_RESULTS.txt"

# 5. Run Graph Generation
echo ""
echo "[*] --------------------------------------------------"
echo "[*] PHASE 2: Generating Academic Validation Graphs"
echo "[*] --------------------------------------------------"
python3 graph_generator.py
echo "[+] All presentation graphs rendered to: testing/graphs/"

echo ""
echo "[*] =================================================="
echo "[*] VALIDATION SUITE COMPLETE. Review VALIDATION_REPORT.md"
echo "[*] =================================================="
