# ⚙️ Sovereignty OS: Master Tech Stack & Dependencies Guide

This master document details every single software component, language, framework, and dependency utilized across the entire lifecycle of the **Smart Home Threat Simulation Platform**. It serves as a comprehensive technical audit for all group members and thesis reviewers.

---

## 1. Hardware & Firmware Layer

This layer acts as the physical, real-world target for our simulations.

### **Hardware Components**
*   **ESP32 Microcontroller (NodeMCU-32S)**: The core processing unit for our Smart Security Hub. Selected for its built-in Wi-Fi and robust IoT capabilities.
*   **PIR Motion Sensor (HC-SR501)**: Connected to the ESP32 to detect physical movement and trigger MQTT telemetry.
*   **Active Buzzer (5V)**: Used as a physical alarm system triggered by MQTT command payloads.

### **Firmware Dependencies**
*   **C++ (Arduino Core)**: The programming language used to write the firmware (`Security_hub.ino`).
*   **PubSubClient (v2.8)**: The C++ library used by the ESP32 to establish and maintain a stable, lightweight connection to the MQTT broker.
*   **WiFi.h**: The standard ESP32 library used to manage the physical WPA2 connection to the local network.

---

## 2. Infrastructure & Networking Layer

This layer handles the complex routing of telemetry between the attacker, the broker, and the AI.

### **Core Infrastructure**
*   **Windows Subsystem for Linux (WSL 2)**: Used to host the entire backend and AI stack natively on Linux (Ubuntu 22.04 LTS) while operating from a Windows host machine.
*   **Eclipse Mosquitto (v2.0+)**: The lightweight, open-source MQTT message broker. It acts as the central hub for all IoT communications. Configured to run on port `1883` allowing anonymous connections for simulation purposes.
*   **iptables (Linux Netfilter)**: The OS-level firewall utility used directly by the AI. When a threat is detected, the AI executes `iptables -A INPUT -s <IP> -j DROP` to drop packets at the kernel level, enforcing our Active Defense.
*   **tcpdump**: A command-line packet analyzer. Called dynamically by the Node.js backend to capture raw `.pcap` files for forensic auditing.

---

## 3. Offensive Security & Telemetry Layer (Python)

This layer generates the 27-feature datasets and executes the cyberattacks.

### **Core Language**
*   **Python 3.12**: The primary language for scripting, automation, and Data Science.

### **Python Dependencies (`requirements.txt`)**
*   **paho-mqtt (v1.6.1+)**: A powerful Python MQTT client. 
    *   *Use:* Utilized by all attack scripts (`bruteforce_attack.py`, `dos_attack_advanced.py`, `replay_attack.py`) and the normal baseline collector to establish connections, publish fake payloads, and subscribe to topics.
*   **socket & os (Python Standard Library)**:
    *   *Use:* `socket` is used in `forensic_utils.py` to dynamically fetch the machine's active WSL IP address via `getsockname()`, ensuring hardcoded IPs never break the simulation. `os` is used for file-system manipulation.
*   **math & collections (Python Standard Library)**:
    *   *Use:* The `math` module calculates Shannon Entropy (`-p * log2(p)`) to measure the randomness of malicious payloads. `collections.deque` is used to maintain sliding windows of the last 100 packets to calculate real-time latency z-scores and inter-arrival standard deviations.

---

## 4. Artificial Intelligence & Data Science Layer

This layer aggregates the data, trains the Random Forest, and executes real-time inference.

### **Cloud Training (Google Colab)**
*   **Google Colab (Jupyter Notebooks)**: The cloud environment used to train the model, utilizing remote CPU/GPU resources to process the massive `combined_ml_dataset.csv`.

### **Data Science Dependencies**
*   **pandas (v2.2+)**: The industry standard data manipulation library.
    *   *Use:* Used in `feature_engineering.py` to merge hundreds of raw CSV files, clean NaN values, and align the 27 columns. Used in `RandomForest_IDS_Training.ipynb` to load the dataset into DataFrames.
*   **scikit-learn (v1.4+)**: The primary Machine Learning library.
    *   *Use:* 
        *   `StandardScaler`: Used to normalize features (e.g., forcing packets_per_second and entropy onto the same variance scale).
        *   `RandomForestClassifier`: The actual ensemble AI algorithm that builds the 100 decision trees to predict the 4 threat labels.
        *   `train_test_split`: Used to divide the dataset into 80% training / 20% testing sets.
        *   `confusion_matrix`: Used to mathematically validate the model's accuracy against False Positives.
*   **numpy (v1.26+)**: Used for high-performance mathematical operations, particularly during Synthetic Data Augmentation (`augment_normal_data.py`) to inject Gaussian noise arrays.
*   **matplotlib & seaborn**:
    *   *Use:* Used exclusively in Colab to generate beautiful, color-coded graphs (Confusion Matrices and Feature Importance charts) for the academic thesis report.
*   **pickle (Python Standard Library)**:
    *   *Use:* Used to serialize (freeze) the trained Random Forest model and Scaler into `.pkl` files, allowing them to be downloaded from the cloud and executed instantly on the Edge gateway.

---

## 5. Enterprise Dashboard & UI Layer

This layer provides a highly professional, real-time command center for the entire platform.

### **Backend Dependencies (Node.js)**
*   **Node.js (v24+)**: The runtime environment.
*   **Express.js (`express v5.2.1`)**: A minimal web framework.
    *   *Use:* Serves the API endpoints (`/api/alert`, `/api/attack/start`) that receive threat notifications from the Python IPS and trigger terminal subprocesses.
*   **Socket.IO (`socket.io v4.8.3`)**: A real-time bidirectional event library.
    *   *Use:* Pushes live telemetry (like latency spikes and firewall drops) directly from the backend to the React frontend with zero latency, eliminating the need for slow HTTP polling.
*   **child_process (Node Standard Library)**:
    *   *Use:* Dynamically spawns Python attack scripts and `tcpdump` processes securely in the background.

### **Frontend Dependencies (React / Vite)**
*   **Vite (`vite v8.0.12`)**: A blazing-fast build tool and development server used instead of Create React App for rapid Hot Module Replacement (HMR).
*   **React (`react v19.2.6`)**: The core UI library used to build the modular dashboard components.
*   **Tailwind CSS (`tailwindcss v3.4.19`)**: A utility-first CSS framework.
    *   *Use:* Used to style the entire dashboard in a dark, "cyber-security" theme with precise grid alignments and hover states.
*   **Recharts (`recharts v3.8.1`)**: A composable charting library built on React components.
    *   *Use:* Powers the Live Network Volumetrics graphs, the Authentication Activity charts, and the Scatter Plots.
*   **Lucide React (`lucide-react v1.16.0`)**: An open-source SVG icon library.
    *   *Use:* Provides the professional icons (Shields, Activity Monitors, Downloads) used throughout the dashboard.
*   **Tailwind Merge & Clsx**: Utility libraries used to conditionally merge Tailwind CSS classes cleanly within React components.

---

## 📅 Project Step-by-Step Execution Flow

For complete clarity, here is the exact chronological execution flow of our entire project architecture:

1.  **Hardware Boot**: The ESP32 boots, connects to Wi-Fi via `WiFi.h`, and establishes an MQTT connection to the Mosquitto broker via `PubSubClient`.
2.  **Baseline Generation**: We execute `normal_traffic_collector.py`, which uses `paho-mqtt` to simulate normal smart home traffic and generates a 27-column `.csv` using Python's `os` and `csv` modules.
3.  **Threat Simulation**: We execute the Attack Suite (`bruteforce_attack.py`, `dos_attack_advanced.py`). Python calculates mathematical entropy (`math`) and sliding window latency (`collections.deque`), dumping massive `.csv` files.
4.  **Feature Alignment**: We run `feature_engineering.py`. `pandas` merges all the raw CSV files into `combined_ml_dataset.csv`.
5.  **Cloud AI Training**: We upload the dataset to Google Colab. `scikit-learn` splits the data, applies `StandardScaler`, and trains the `RandomForestClassifier`. `pickle` exports the intelligence as `.pkl` files.
6.  **Edge IPS Deployment**: We download the `.pkl` files to the local machine. We run `live_ml_ips.py` with `sudo`. It loads the models into memory and begins sniffing local network traffic.
7.  **Dashboard Initialization**: We launch `server.js` (Express + Socket.IO) and `npm run dev` (Vite + React + Tailwind). The user interface connects to the backend.
8.  **The Climax (Autonomous Defense)**: The user clicks "Brute Force" on the UI. The Node backend uses `child_process` to run the Python attack. `live_ml_ips.py` intercepts the traffic, predicts an attack in <10ms, executes an OS-level `iptables DROP` command, and posts an alert to the Express API. The API uses Socket.IO to push the alert to the React UI, which flashes red and updates the Recharts graphs instantly.

*(End of Technical Audit).*
