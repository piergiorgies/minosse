import asyncio
import aio_pika
import json
import requests
import time

from src.judge import execute_code_locally
from src.config_loader import load_config
from src.util import get_auth_headers
from src.logger import get_logger
from src.models.submission_dto import SubmissionDTO
from src.models.errors import CompilationError, EXECUTION_RESULTS

config = load_config()
logger = get_logger()

async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        logger.info('Submission received')

        try:
            # data = json.loads(message.body.decode())
            
            # if 'code' not in data:
            #     logger.error('submitted_code not specified')
            #     return
            # if 'problem_id' not in data:
            #     logger.error('problem_id not specified')
            #     return
            # if 'language' not in data:
            #     logger.error('language_id not specified')
            #     return
            # if 'submission_id' not in data:
            #     logger.error('id not specified')
            #     return
            try:
                body = json.loads(message.body.decode())
                submission_dto = SubmissionDTO(**body)
            except Exception as e:
                print(f'Error while parsing the submission data: {e}')
                return

            # is_pretest_run = 'is_pretest_run' in data and data['is_pretest_run']
            is_pretest_run = submission_dto.is_pretest_run
            
            try:
                # execution_result = execute_code_locally(data['code'], data['problem_id'], data['language'], data['submission_id'], is_pretest_run)
                execution_result = execute_code_locally(submission_dto)
                submission_result = 0

                for result in execution_result['results']:
                    submission_result = max(submission_result, result['result_id'])
                
                data_to_send = {'result_id': submission_result, 'stderr': ''}

            except CompilationError as e:
                submission_result = EXECUTION_RESULTS['COMPILATION_ERROR']
                data_to_send = {'result_id': submission_result, 'stderr': e.stderr}

            sent = False
            api_url = config['send_total_submission_result_api']
            api_url = api_url.format(submission_id=data['submission_id'])
            for _ in range(3):
                try:
                    response = requests.post(api_url, json=data_to_send, headers=get_auth_headers())
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

            rabbitmq_host = config.rabbitmq_host
            rabbitmq_user = config.rabbitmq_user
            rabbitmq_pass = config.rabbitmq_pass
            connection = await aio_pika.connect_robust(f'amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}/')
            
            # If connection is successful, proceed
            async with connection:
                # Create a channel
                channel = await connection.channel()

                # Declare the queue where the messages will be consumed from
                queue = await channel.declare_queue('submissions', durable=True)

                # Start consuming messages from the queue
                await queue.consume(callback)

                # Keep the connection open for consumption
                logger.info(" [*] Waiting for messages...")
                await asyncio.Future()  # Infinite loop to keep the script running

        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            logger.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(5)  # Retry after some delay in case of an unexpected error