#!/bin/bash

# ───────────────────────────────────────────────
# 🌐 Ask for Target URL
read -p "🔗 Enter target URL (e.g., https://example.com): " TARGET_URL

# 📄 Ask for Wordlist path
read -p "📂 Enter path to wordlist (e.g., /usr/share/seclists/...): " WORDLIST

# 🧩 File extensions to test (compressed, no spaces)
EXTS=$(echo ".php,.asp,.aspx,.jsp,.cgi,.pl,.py,.rb,.go,.conf,.cfg,.ini,.yaml,.yml,.json,.xml,.env,.bak,.old,.backup,.zip,.tar,.tar.gz,.rar,.7z,.txt,.log,.md,.csv,.sql,.db,.sqlite,.sqlite3,.test,.dev,.temp,.tmp,.example,.sample,.swp,.orig,.html,.htm,.js,.css,.map,.git,.svn,.DS_Store,.htaccess,.htpasswd,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.pem,.crt,.key,.p12,.pfx" | tr -d ' ')

# 🏁 Start the scan
echo -e "\n🚀 Starting feroxbuster scan on $TARGET_URL ..."
feroxbuster -u "$TARGET_URL" \
  -w "$WORDLIST" \
  -x "$EXTS" \
  -r -t 100 --depth 3 \
  --status-codes 200,204,301,302,403 \
  -o "ferox-output.txt"

# 📦 Done!
echo -e "\n✅ Scan complete. Output saved to: ferox-output.txt"
