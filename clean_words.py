import os
import re

files_to_clean = []
for root, dirs, files in os.walk('/home/pirator/smart-home-threat-simulation-platform'):
    if 'dataset/logs' in root:
        continue
    for file in files:
        if file.endswith('.py') or file.endswith('.ino'):
            files_to_clean.append(os.path.join(root, file))

replacements = {
    r'Smart Home Threat Simulation Platform: Active ML-IPS Node': 'Smart Home Threat Simulation Platform: Active ML-IPS Node',
    r'Smart Home Threat Simulation Platform: Automated Replay Attack': 'Smart Home Threat Simulation Platform: Automated Replay Attack',
    r'Smart Home Threat Simulation Platform: Distributed DoS Simulator': 'Smart Home Threat Simulation Platform: Distributed DoS Simulator',
    r'Smart Home Threat Simulation Hub': 'Smart Home Threat Simulation Hub',
    r'Smart Home Threat Simulation Forensic Utility': 'Smart Home Threat Simulation Forensic Utility',
    r'Smart Home ML-IDS Replay Attack': 'Smart Home ML-IDS Replay Attack',
    r'Smart Home Threat Simulation Platform': 'Smart Home Threat Simulation Platform',
    r'Smart Home Threat Simulation Platform': 'Smart Home Threat Simulation Platform',
    r'(?i)\bsovereign(ty)?\b': 'Smart Home Threat Simulation Platform',
    r'(?i)advanced': 'advanced',
    r'(?i)advanced': 'advanced',
    r'(?i)professional': 'professional',
    r'(?i)high': 'high',
}

for file_path in files_to_clean:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        for pattern, repl in replacements.items():
            new_content = re.sub(pattern, repl, new_content)
            
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Cleaned {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
print("Cleanup done!")
