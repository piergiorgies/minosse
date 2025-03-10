import asyncio
import aio_pika
import json
import requests
import time

from src.judge import execute_code_locally, execute_public_test_cases
from src.config_loader import load_config
from src.util import get_auth_headers
from src.logger import get_logger

config = load_config()
logger = get_logger()

async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        logger.info('Submission received')

        try:
            data = json.loads(message.body.decode())
            
            if 'code' not in data:
                logger.error('submitted_code not specified')
                # print('submitted_code not specified')
                return
            if 'problem_id' not in data:
                logger.error('problem_id not specified')
                # print('problem_id not specified')
                return
            if 'language' not in data:
                logger.error('language_id not specified')
                # print('language_id not specified')
                return
            if 'submission_id' not in data:
                logger.error('id not specified')
                # print('id not specified')
                return

            if 'is_pretest_run' in data and data['is_pretest_run']:
                execution_result = execute_public_test_cases(data['code'], data['problem_id'], data['language'], data['submission_id'])
            else:
                execution_result = execute_code_locally(data['code'], data['problem_id'], data['language'], data['submission_id'])
            submission_result = 0
            for result in execution_result['results']:
                submission_result = max(submission_result, result['result_id'])

            sent = False
            api_url = config['send_total_submission_result_api']
            api_url = api_url.format(submission_id=data['submission_id'])
            for _ in range(3):
                try:
                    response = requests.post(api_url, json={'result_id': submission_result}, headers=get_auth_headers())
                    if response.status_code != 200:
                        time.sleep(0.2)
                    else:
                        sent = True
                        break
                except Exception as e:
                    pass

            if not sent:
                logger.error(f'Failed in sending submission total {data["submission_id"]}')

        except Exception as e:
            logger.error(f'Error while processing submission: {e}')
            # print(e)

async def start_listen_for_submissions():
    while True:
        try:
            # Attempt to connect to RabbitMQ
            logger.info("Trying to connect to RabbitMQ...")
            # print("Trying to connect to RabbitMQ...")
            connection = await aio_pika.connect_robust(f'amqp://{config['rabbitmq_user']}:{config['rabbitmq_pass']}@{config['rabbitmq_host']}/')
            
            # If connection is successful, proceed
            async with connection:
                # Create a channel
                channel = await connection.channel()

                # Declare the queue where the messages will be consumed from
                queue = await channel.declare_queue('submissions', durable=True)

                # Start consuming messages from the queue
                await queue.consume(callback)

                # Keep the connection open for consumption
                # print(" [*] Waiting for messages. To exit press CTRL+C")
                logger.info(" [*] Waiting for messages...")
                await asyncio.Future()  # Infinite loop to keep the script running

        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            # print(f"Failed to connect to RabbitMQ: {e}")
            logger.info("Retrying in 5 seconds...")
            # print(f"Retrying in 5 seconds...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            # print(f"Unexpected error: {e}")
            await asyncio.sleep(5)  # Retry after some delay in case of an unexpected error