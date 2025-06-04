import sys
import socket
import threading
from scapy.all import IP, TCP, sr1, conf
from queue import Queue
import time
import os

conf.verb = 0  # Disable Scapy output
THREAD_COUNT = 100
START_PORT = 1
END_PORT = 65535
port_queue = Queue()

def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[-] Could not resolve {target}")
        return None

def scan_port(target_ip, port, open_ports):
    pkt = IP(dst=target_ip)/TCP(dport=port, flags="S")
    resp = sr1(pkt, timeout=0.5, verbose=0)

    if resp is not None and resp.haslayer(TCP):
        if resp[TCP].flags == 0x12:
            open_ports.append(port)
            rst_pkt = IP(dst=target_ip)/TCP(dport=port, flags="R")
            sr1(rst_pkt, timeout=0.2, verbose=0)
            print(f"[+] {target_ip} - Open port: {port}")

def worker(target_ip, open_ports):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(target_ip, port, open_ports)
        port_queue.task_done()

def scan_target(target):
    ip = resolve_target(target)
    if not ip:
        return

    print(f"\n[~] Scanning {target} ({ip})")
    start = time.time()

    for port in range(START_PORT, END_PORT + 1):
        port_queue.put(port)

    open_ports = []
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(ip, open_ports))
        t.start()
        threads.append(t)

    port_queue.join()
    duration = time.time() - start

    print(f"[✔] Done scanning {target} in {duration:.2f} seconds.")
    if open_ports:
        print(f"[+] Open ports: {sorted(open_ports)}")
        with open("scan_results.txt", "a") as f:
            f.write(f"\n{target} ({ip}): {sorted(open_ports)}\n")
    else:
        print("[-] No open ports found.")

def main():
    print("\n=== Stealth Port Scanner ===")
    print("1. Enter IP/domain/subdomain")
    print("2. Enter filename with list of targets")
    choice = input("Choose (1 or 2): ").strip()

    if choice == '1':
        target = input("Enter IP, domain, or subdomain: ").strip()
        scan_target(target)
    elif choice == '2':
        filename = input("Enter filename: ").strip()
        if not os.path.isfile(filename):
            print("[-] File not found.")
            return
        with open(filename, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
            for target in targets:
                scan_target(target)
    else:
        print("[-] Invalid choice.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Please run this script as root (required for raw sockets).")
        sys.exit(1)
    main()
