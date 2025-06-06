#!/bin/bash

# Ask for the file path that contains the list of JS URLs
read -p "Enter the path to the file containing JS URLs: " URL_FILE

# Check if the file exists
if [[ ! -f "$URL_FILE" ]]; then
  echo "❌ File not found: $URL_FILE"
  exit 1
fi

# Directory to store downloaded JS files
OUTPUT_DIR="downloaded_js"
mkdir -p "$OUTPUT_DIR"

echo "📥 Downloading JS files listed in $URL_FILE ..."

# Read each URL from the file and download
while IFS= read -r url || [[ -n "$url" ]]; do
  [[ -z "$url" ]] && continue  # skip empty lines
  filename=$(basename "$url")
  echo "🔻 Downloading $filename ..."
  curl -s -o "$OUTPUT_DIR/$filename" "$url"
done < "$URL_FILE"

echo "✅ All files downloaded into ./$OUTPUT_DIR"
