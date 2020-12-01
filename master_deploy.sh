gcloud functions deploy \
    poll-webhook-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-topic=poll-webhook-topic \
        --timeout=539 \
        --env-vars-file=/home/nicolas/projects/janium/python/functions/envs.yaml \
        --source=/home/nicolas/projects/janium/python/functions/poll_webhook/ \
        --egress-settings=private-ranges-only \
        --vpc-connector=janium-vpc-connector \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/poll-webhook-function.log 2>&1 &

gcloud functions deploy \
    director-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-topic=janium-main-topic \
        --timeout=539 \
        --env-vars-file=/home/nicolas/projects/janium/python/functions/envs.yaml \
        --source=/home/nicolas/projects/janium/python/functions/director/ \
        --egress-settings=private-ranges-only \
        --vpc-connector=janium-vpc-connector \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/director-function.log 2>&1 &

gcloud functions deploy \
    send-email-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-topic=send-email-topic \
        --timeout=539 \
        --env-vars-file=/home/nicolas/projects/janium/python/functions/envs.yaml \
        --source=/home/nicolas/projects/janium/python/functions/send_email/ \
        --egress-settings=private-ranges-only \
        --vpc-connector=janium-vpc-connector \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/send-email-function.log 2>&1 &

gcloud functions deploy \
    track-email-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-http \
        --timeout=539 \
        --env-vars-file=/home/nicolas/projects/janium/python/functions/envs.yaml \
        --source=/home/nicolas/projects/janium/python/functions/track_email/ \
        --allow-unauthenticated \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/track-email-function.log 2>&1 &

gcloud functions deploy \
    send-daily-tasks-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-topic=send-daily-tasks-topic \
        --timeout=539 \
        --env-vars-file=/home/nicolas/projects/janium/python/functions/envs.yaml \
        --source=/home/nicolas/projects/janium/python/functions/send_daily_tasks/ \
        --egress-settings=private-ranges-only \
        --vpc-connector=janium-vpc-connector \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/send-daily-tasks-function.log 2>&1 &

gcloud functions deploy \
    send-test-email-function \
        --region=us-central1 \
        --entry-point=main \
        --runtime=python38 \
        --trigger-http \
        --timeout=539 \
        --source=/home/nicolas/projects/janium/python/functions/send_test_email/ \
    >> /home/nicolas/projects/janium/python/master_deploy_logs/send-test-email-function.log 2>&1 &