import pika
import json
import requests
import time

from judge import execute_code_locally
from config_loader import load_config

config = load_config()

def callback(channel, method, properties, body):
    try:
        data = json.loads(body)
        
        if 'code' not in data:
            print('code not specified')
            return
        if 'problem_id' not in data:
            print('problem_id not specified')
            return
        if 'language' not in data:
            print('language not specified')
            return

        if 'submission_id' not in data:
            print('submission_id not specified')
            return

        execution_result = execute_code_locally(data['code'], data['problem_id'], data['language'], data['submission_id'])
        submission_result = 0
        for result in execution_result:
            submission_result = max(submission_result, result['result_id'])


        sent = False
        api_url = config['send_total_submission_result_api']
        api_url = api_url.format(submission_id=data['submission_id'])
        for _ in range(3):
            response = requests.post(api_url, json={'result_id': submission_result})
            if response.status_code != 200:
                time.sleep(0.2)
            else:
                sent = True
                break

        if not sent:
            print(f'Failed in sending submission {data['submission_id']}')

    except Exception as e:
        print(e)


# TODO: manage a global connection and check if there are problems every 30 seconds
def start_listen_for_submissions():
    credentials = pika.PlainCredentials(config['rabbitmq_user'], config['rabbitmq_pass']) 
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbitmq_host'], credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='submissions')
    channel.basic_consume(queue='submissions', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()