import pika
import json

from judge import execute_code_locally

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

        execution_result = execute_code_locally(data['code'], data['problem_id'], data['language'])
        print(execution_result  )
    except Exception as e:
        print(e)


def start_listen_for_submissions():
    credentials = pika.PlainCredentials('apo', 'ApoChair2023!') 
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='submissions')
    channel.basic_consume(queue='submissions', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()