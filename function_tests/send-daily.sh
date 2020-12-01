payload_path="/home/nicolas/projects/janium/python/tests/send_daily_tasks.json"
echo "Where should this message send from? (from which publisher)"
read from
echo "$from"
payload=$(jq --arg from "$from" '.from = $from' "$payload_path")
echo "$payload"

gcloud pubsub topics publish send-daily-tasks-topic --message "$payload"
