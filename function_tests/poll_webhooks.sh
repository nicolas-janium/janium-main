payload_path="/home/nicolas/projects/janium/python/function_tests/poll_webhooks.json"
echo "Where should this message send from?"
read from
echo "$from"
payload=$(jq --arg from "$from" '.from = $from' "$payload_path")
# echo "$payload"

gcloud pubsub topics publish poll-webhook-topic --message "$payload"
