payload_path="/home/nicolas/projects/janium/python/tests/send_email_payload.json"
echo "Where should this message send from?"
read from
echo "$from"
payload=$(jq --arg from "$from" '.from = $from' "$payload_path")
echo "$payload"

gcloud pubsub topics publish send-email-topic --message "$payload"
