#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from termcolor import cprint

# Base output folder
OUTPUT_DIR = Path("recon-output")
OUTPUT_DIR.mkdir(exist_ok=True)

def banner():
    cprint("\n[+] WHOIS & DNS Recon Automation (BlackArch Edition)", "cyan", attrs=["bold"])
    cprint("    by H4K2LIV3\n", "magenta")

def run_command(command, title, output_file):
    cprint(f"\n[>] {title}", "yellow", attrs=["bold"])
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        print(result.stdout)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n[ERRORS]\n" + result.stderr)
    except subprocess.TimeoutExpired:
        cprint("[-] Command timed out", "red")
    except Exception as e:
        cprint(f"[-] Error: {str(e)}", "red")

def main(domain):
    banner()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    domain_dir = OUTPUT_DIR / f"{domain}_{timestamp}"
    domain_dir.mkdir(parents=True, exist_ok=True)

    tools = [
        (f"whois {domain}", "WHOIS Info", "whois.txt"),
        (f"amass enum -d {domain} -o -", "Amass Subdomain Enumeration", "amass.txt"),
        (f"theharvester -d {domain} -b all", "theHarvester Emails & Users", "harvester.txt"),
        (f"dig {domain} any +noall +answer", "DIG Records (ANY)", "dig_any.txt"),
        (f"dig mx {domain}", "DIG MX Records", "dig_mx.txt"),
        (f"dig txt {domain}", "DIG TXT Records", "dig_txt.txt"),
        (f"nslookup -type=any {domain}", "Nslookup ANY", "nslookup_any.txt"),
        (f"dnsrecon -d {domain}", "DNSRecon Scan", "dnsrecon.txt"),
        (f"perl -Mno warnings::deprecated -S dnsenum {domain}", "DNSEnum Scan", "dnsenum.txt")
    ]



    for cmd, desc, fname in tools:
        run_command(cmd, desc, domain_dir / fname)

    cprint(f"\n[✓] All recon data saved in: {domain_dir}\n", "green", attrs=["bold"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        cprint("Usage: python3 blackarch_recon.py <domain.com>\n", "red", attrs=["bold"])
        sys.exit(1)
    main(sys.argv[1])
