# 🧠 Machine Learning & IPS Deployment Guide

This guide details the exact steps to transition from raw simulation data to a fully deployed **Active Defense Intrusion Prevention System (ML-IPS)**. It leverages a Cloud-to-Edge architecture, utilizing Google Colab for heavy-lifting data science, and local Python scripts for real-time edge execution.

---

## Phase 1: Feature Engineering & Dataset Aggregation

Once you have generated raw telemetry logs using the scripts in the [Attack Suite Guide](ATTACK_SUITE_GUIDE.md), you must aggregate them into a single, standardized CSV file for the machine learning model.

Our custom `feature_engineering.py` script automatically:
1. Scans `dataset/logs/` for all Normal, Brute Force, DoS, and Replay `.csv` files.
2. Cleans missing or broken sliding-window variables.
3. Merges the files and outputs the final master dataset.

**Execution Command:**
```bash
python3 dataset/feature_engineering.py
```
* **Output:** `dataset/combined_ml_dataset.csv` (This file will be large, often ~15MB to 50MB).

---

## Phase 2: Cloud Model Training (Google Colab)

To demonstrate a professional Data Science workflow for your Master's thesis, the Random Forest model is trained in the cloud. This provides perfectly rendered `matplotlib` and `seaborn` graphs (Confusion Matrices and Feature Importance charts) that you can copy directly into your academic report.

### Step-by-Step Instructions:
1. **Upload Dataset to Drive:** Upload your generated `combined_ml_dataset.csv` into a folder named **`Colab Notebooks`** in your Google Drive.
2. **Upload Notebook:** Upload the `RandomForest_IDS_Training.ipynb` file into the exact same folder.
3. **Launch Colab:** Double-click the `.ipynb` file in Google Drive to open it in Google Colab.
4. **Train:** Click **Runtime > Run All** at the top of the screen.
5. **Authenticate:** A popup will ask to mount your Google Drive. Click "Allow" so the script can read the CSV file.
6. **Review Metrics:** Scroll through the notebook to verify your model achieved >95% accuracy on the test split. Take screenshots of the Confusion Matrix!
7. **Download Models:** The notebook will automatically save two files back into your Google Drive:
   * `random_forest_ids.pkl` (The mathematical decision tree).
   * `scaler.pkl` (The normalizer required for live data).
   
Download these two `.pkl` files and place them in the root of your local `smart-home-threat-simulation-platform` directory.

---

## Phase 3: Active Defense (Live ML-IPS Deployment)

With the trained intelligence (the `.pkl` files) now running locally on the Edge, we can activate the Intrusion Prevention System. 

The `live_ml_ips.py` script acts as a real-time firewall. It sniffs the network telemetry, mathematically scales the 15 features, passes them into the Random Forest model, and if it predicts an attack (`1`, `2`, or `3`), it instantly neuters the attacker at the OS level using `iptables`.

**Execution Command:**
```bash
sudo python3 defence/live_ml_ips.py
```
*(Note: `sudo` privileges are strictly required because the script actively modifies Linux firewall rules).*

### Thesis Demonstration Strategy:
To impress your panel, follow this exact sequence:
1. Open two terminal windows side-by-side.
2. In Terminal A, start the defense: `sudo python3 defence/live_ml_ips.py`
3. In Terminal B, launch an aggressive attack: `python3 attacks/bruteforce_attack.py --broker 192.168.21.120 --userlist dataset/userlist_bruteforce.txt --file dataset/wordlist_10k.txt --threads 10`
4. **The Result:** Watch Terminal A instantly detect the threat signature and execute a `DROP` command against Terminal B's IP address. Terminal B will immediately crash with "Connection Refused" errors, proving the Active Defense is 100% operational.

---

*“Building the future of IoT security, one simulation at a time.”*
