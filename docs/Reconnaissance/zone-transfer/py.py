import dns.query
import dns.zone
import dns.resolver
import sys
from datetime import datetime

OUTPUT_FILE = "zone_transfer_results.txt"

def find_zone_root(domain):
    parts = domain.split('.')
    for i in range(len(parts) - 1):
        test_domain = '.'.join(parts[i:])
        try:
            dns.resolver.resolve(test_domain, 'NS')
            return test_domain
        except:
            continue
    return None

def attempt_zone_transfer(domain):
    print(f"\n[+] Looking for NS records for: {domain}")
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        nameservers = [str(rdata.target).strip('.') for rdata in answers]
    except Exception as e:
        print(f"[-] Failed to resolve NS records: {e}")
        return

    success = False
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"\n--- Zone Transfer Attempt for {domain} ---\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Nameservers: {', '.join(nameservers)}\n")

        for ns in nameservers:
            try:
                print(f"\n[+] Trying zone transfer from NS: {ns}")
                zone = dns.zone.from_xfr(dns.query.xfr(ns, domain, lifetime=5))
                if zone:
                    print(f"[!] Zone transfer SUCCESS from {ns}")
                    f.write(f"\n[!] Zone transfer SUCCESS from {ns}\n")
                    for name, node in zone.nodes.items():
                        rdatasets = node.rdatasets
                        for rdataset in rdatasets:
                            full_name = f"{name}.{domain}" if str(name) != '@' else domain
                            line = f"{full_name} - {rdataset}"
                            print(line)
                            f.write(line + "\n")
                    success = True
                else:
                    print(f"[-] Empty zone transfer from {ns}")
            except Exception as e:
                print(f"[-] Zone transfer from {ns} failed: {e}")
                f.write(f"[-] Zone transfer from {ns} failed: {e}\n")

    if not success:
        print("\n[-] No successful zone transfers found.")
    else:
        print(f"\n[+] Results saved in '{OUTPUT_FILE}'")

if __name__ == "__main__":
    print("🔎 DNS Zone Transfer Automation Tool")
    domain_input = input("Enter your target domain (e.g., example.com): ").strip().lower()
    
    zone_root = find_zone_root(domain_input)
    if not zone_root:
        print("[-] Could not find a valid DNS zone to test.")
        sys.exit(1)
    
    print(f"[+] Discovered zone root: {zone_root}")
    attempt_zone_transfer(zone_root)
