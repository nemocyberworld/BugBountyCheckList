while read url; do
  status=$(curl -o /dev/null -s -w "%{http_code}" "$url")
  if [[ "$status" == "200" || "$status" == "301" || "$status" == "302" ]]; then
    echo "$status $url"
  fi
done < wayback.txt
