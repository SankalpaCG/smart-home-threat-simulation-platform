# Run System

This is the clean entry point for the real-hardware demo and the broader research platform.

## Folder Map

```text
smart-home-threat-simulation-platform/
  attacks/              Attack simulations plus attack analysis tools
  defence/              Logger, IDS, guard, and probe tools
  demo/                 Data collection, DoS launcher, and demo utilities
  dataset/labeled/      Simple labeled CSVs: Normal and DoS
  dataset/raw/          Generated telemetry and raw logs
  dataset/logs/         Attack/defence summaries
  dataset/sessions/     Per-run forensic sessions
  docs/                 Guides, demo notes, and research notes
  firmware/             ESP32 sketches and Wokwi projects
  reports/              Generated performance reports
  scripts/              Setup/helper scripts
```

## Real-Hardware Security Hub Demo

1. Upload this firmware to the ESP32:

```text
firmware/security-hub-real/Security_hub.ino
```

Use Arduino IDE with the ESP32 on `COM3` if that is still the connected port.

2. Start Mosquitto/MQTT broker on the PC.

3. Open a terminal in `demo/` for collection and DoS tests.

4. Collect normal or attack telemetry:

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe data_collector.py
```

5. Run the DoS demo:

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe dos_attack.py
```

6. Run the replay demo:

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe ..\attacks\replay_attack.py
```

7. Analyze the labeled CSVs:

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe ..\attacks\attack_comparator.py
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe ..\attacks\replay_detector.py
```

## Important Notes

- `dataset/labeled/dataset_Normal.csv` uses label `0`.
- `dataset/labeled/dataset_DoS.csv` uses label `1`.
- Demo reports are written to `reports/`.
- The current normal dataset is very repetitive, so replay detection still flags it as suspicious. Recollect a richer normal baseline before relying on model accuracy.
- `.env` is local configuration and should not be committed with real credentials.
