#!/usr/bin/env python3

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from termcolor import cprint, colored

def fetch_robots_txt(domain):
    url = urljoin(domain, "/robots.txt")
    cprint(f"\n[*] Fetching robots.txt from {url}", "cyan")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            cprint(f"[-] robots.txt not found (status {response.status_code})", "yellow")
            return []
        paths = []
        for line in response.text.splitlines():
            if line.lower().startswith("disallow:"):
                path = line.split(":")[1].strip()
                if path:
                    paths.append(path)
        return paths
    except Exception as e:
        cprint(f"[-] Error fetching robots.txt: {e}", "red")
        return []

def fetch_sitemap_urls(domain):
    url = urljoin(domain, "/sitemap.xml")
    cprint(f"\n[*] Fetching sitemap.xml from {url}", "cyan")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            cprint(f"[-] sitemap.xml not found (status {response.status_code})", "yellow")
            return []
        soup = BeautifulSoup(response.text, "xml")
        return [loc.text.strip() for loc in soup.find_all("loc")]
    except Exception as e:
        cprint(f"[-] Error fetching sitemap.xml: {e}", "red")
        return []

def check_url_status(full_url):
    try:
        response = requests.head(full_url, timeout=10, allow_redirects=True)
        return response.status_code
    except Exception:
        return "Error"

def main():
    cprint("\n=== 🔍 Content Discovery (robots.txt & sitemap.xml) ===", "green", attrs=["bold"])
    domain = input("\n🌐 Enter the target domain (e.g., https://example.com): ").strip()
    if not domain.startswith("http"):
        domain = "https://" + domain

    discovered_urls = []

    # Robots.txt
    robots_paths = fetch_robots_txt(domain)
    if robots_paths:
        cprint(f"\n[+] Found {len(robots_paths)} disallowed paths in robots.txt:", "green")
        for path in robots_paths:
            full_url = urljoin(domain, path)
            status = check_url_status(full_url)
            color = "green" if status == 200 else "yellow" if status == 403 else "red"
            cprint(f"  [ {status} ] {full_url}", color)
            discovered_urls.append((full_url, status))
    else:
        cprint("[-] No disallowed paths found in robots.txt.", "yellow")

    # Sitemap.xml
    sitemap_urls = fetch_sitemap_urls(domain)
    if sitemap_urls:
        cprint(f"\n[+] Found {len(sitemap_urls)} URLs in sitemap.xml:", "green")
        for url in sitemap_urls:
            status = check_url_status(url)
            color = "green" if status == 200 else "yellow" if status == 403 else "red"
            cprint(f"  [ {status} ] {url}", color)
            discovered_urls.append((url, status))
    else:
        cprint("[-] No URLs found in sitemap.xml.", "yellow")

    # Save results
    if discovered_urls:
        with open("discovered_content.txt", "w") as f:
            for url, status in discovered_urls:
                f.write(f"{status} {url}\n")
        cprint(f"\n📁 Results saved to discovered_content.txt\n", "cyan")
    else:
        cprint("\n[!] No URLs discovered to save.\n", "yellow")

if __name__ == "__main__":
    main()
