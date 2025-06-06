#!/bin/bash

# ---------------------------------------
# 🔎 JavaScript Recon & Secrets Extractor
# ---------------------------------------
# Dependencies: waybackurls, curl, linkfinder, secretfinder, js-beautify

echo -e "\n\033[1;36m🚀 JavaScript Analysis Automation Script\033[0m"
read -rp $'\033[1;33mEnter your target domain (e.g., example.com): \033[0m' TARGET

if [ -z "$TARGET" ]; then
  echo -e "\033[1;31m[!] No domain entered. Exiting.\033[0m"
  exit 1
fi

# Prepare directories
mkdir -p js-files extracted/endpoints extracted/secrets beautified

# Step 1: Get JavaScript file URLs
echo -e "\n\033[1;34m[1] 🔍 Fetching JavaScript URLs from Wayback Machine...\033[0m"
waybackurls "$TARGET" | grep '\.js$' | sort -u > js-urls.txt
echo -e "\033[1;32m[+] Found $(wc -l < js-urls.txt) JS files.\033[0m"

# Step 2: Download JS files
echo -e "\n\033[1;34m[2] 📥 Downloading JS files...\033[0m"
cd js-files || exit 1
while read -r url; do
  filename=$(echo "$url" | sed 's/[^a-zA-Z0-9]/_/g')
  echo -e "\033[1;32m[+] Downloading:\033[0m $url"
  curl -s "$url" -o "$filename.js"
done < ../js-urls.txt
cd ..

# Step 3: Extract endpoints
echo -e "\n\033[1;34m[3] 📡 Extracting Endpoints using LinkFinder...\033[0m"
for file in js-files/*.js; do
  name=$(basename "$file")
  echo -e "\033[1;33m[*] Analyzing:\033[0m $name"
  linkfinder -i "$file" -o cli > "extracted/endpoints/$name.endpoints.txt"
done

# Step 4: Extract secrets
echo -e "\n\033[1;34m[4] 🔑 Extracting Secrets using SecretFinder...\033[0m"
for file in js-files/*.js; do
  name=$(basename "$file")
  echo -e "\033[1;33m[*] Analyzing:\033[0m $name"
  secretfinder -i "$file" -o cli > "extracted/secrets/$name.secrets.txt"
done

# Step 5: Beautify JS files
echo -e "\n\033[1;34m[5] 🎨 Beautifying JS files using js-beautify...\033[0m"
for file in js-files/*.js; do
  name=$(basename "$file")
  if command -v js-beautify >/dev/null 2>&1; then
    js-beautify "$file" > "beautified/$name.pretty.js"
  else
    echo -e "\033[1;31m[!] js-beautify not found. Skipping beautification for $name.\033[0m"
  fi
done

# Summary
echo -e "\n\033[1;32m✅ Done! Summary of output:\033[0m"
echo -e "  📁 JS Files:       ./js-files/"
echo -e "  📄 Endpoints:      ./extracted/endpoints/"
echo -e "  🔐 Secrets:        ./extracted/secrets/"
echo -e "  🎨 Beautified JS:  ./beautified/"
