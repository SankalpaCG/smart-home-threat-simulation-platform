# 🚀 Quick Start Guide - Running Scripts

## Method 1: Use Batch Files (Easiest for Windows)

Simply **double-click** any of these files from the project directory:

```
📁 Security_hub/
├── replay_attack.bat          ← Double-click to run
├── replay_detector.bat        ← Double-click to run
├── attack_comparator.bat      ← Double-click to run
├── data_collector.bat         ← Double-click to run
├── dos_attack.bat             ← Double-click to run
└── run.bat                    ← Universal script runner
```

**Example:**
```
Double-click: replay_attack.bat
→ Script runs automatically
→ Select attack mode (1-4)
→ Watch the attack execute
```

---

## Method 2: Use PowerShell Aliases (Recommended for Developers)

### Setup (One-time):

1. **Open PowerShell as Administrator**
2. **Run the setup script:**
   ```powershell
   C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub\setup-powershell.ps1
   ```

3. **Or manually add to your PowerShell profile:**
   ```powershell
   # Edit your profile
   notepad $PROFILE
   
   # Add this content from setup-powershell.ps1
   ```

### After Setup, Use Simple Commands:

```powershell
# Navigate to project (if not already there)
cd "C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub"

# Run any script with simple commands
replay-attack
replay-detector
attack-compare
data-collect
dos-attack
```

---

## Method 3: Use `run.bat` Universal Runner

From the project directory:

```cmd
rem Show help
run

rem Run specific script
run replay_attack.py
run replay_detector.py
run attack_comparator.py
run data_collector.py
run dos_attack.py

rem With arguments (if needed)
run replay_attack.py --help
```

---

## Method 4: Manual Command Line (Full Path)

From any directory:

```powershell
cd "C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub"
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe replay_attack.py
```

---

## Environment Variables

A `.env` file has been created with the following variables:

```
PYTHON_PATH=C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe
PROJECT_DIR=C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=shtsp/home/telemetry
```

You can reference these in scripts or your IDE.

---

## Comparison of Methods

| Method | Ease | IDE Support | Cross-Platform |
|--------|------|-------------|-----------------|
| **Batch Files** | ⭐⭐⭐⭐⭐ | Limited | Windows only |
| **PowerShell** | ⭐⭐⭐⭐ | Good | Windows only |
| **run.bat** | ⭐⭐⭐ | Good | Windows only |
| **Full Path** | ⭐ | Excellent | All platforms |

---

## Quick Reference

**Windows (Easiest):**
```
1. Open project folder in Explorer
2. Double-click replay_attack.bat
3. Done! 🎉
```

**PowerShell (Recommended):**
```powershell
replay-attack
replay-detector
attack-compare
```

**VS Code (Integrated Terminal):**
```
1. Open VS Code
2. Terminal → New Terminal
3. Type: replay-attack
4. Press Enter
```

---

## Troubleshooting

**Error: Python not found**
- Make sure Python 3.14 is installed at: `C:\Users\Test\AppData\Local\Programs\Python\Python314`
- Edit the batch files and update the path if needed

**Error: MQTT connection failed**
- Make sure Mosquitto broker is running
- Start it with: `mosquitto`

**Error: Module not found (paho-mqtt)**
- Install it: `pip install paho-mqtt`
- Or: `C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe -m pip install paho-mqtt`

---

## Files Created

```
📁 Project Root/
├── run.bat                    - Universal script runner
├── replay_attack.bat          - Batch shortcut
├── replay_detector.bat        - Batch shortcut
├── attack_comparator.bat      - Batch shortcut
├── data_collector.bat         - Batch shortcut
├── dos_attack.bat             - Batch shortcut
├── setup-powershell.ps1       - PowerShell profile setup
├── .env                       - Environment variables
└── QUICKSTART.md              - This file!
```

---

## Next Steps

1. **Try Method 1 (Batch Files):**
   - Double-click `replay_attack.bat`
   - Select attack mode `1`
   - Watch it run!

2. **For development, use Method 2 (PowerShell):**
   - Run `setup-powershell.ps1`
   - Use simple commands like `replay-attack`

3. **For CI/CD, use Method 4 (Full Path):**
   - Full path works everywhere
   - No setup required

---

**Happy Hacking! 🔐**
