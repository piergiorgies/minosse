import requests
import os
import yaml

from src.config_loader import load_config
from src.util import get_auth_headers
from src.logger import get_logger

logger = get_logger()
config = load_config()
problem_versions = {}
endpoint_timeout = 1

def update_problem_config(problem_id):
    api_url = config['get_problem_config_api']
    api_url = api_url.format(problem_id=problem_id)   
    
    response = requests.post(api_url, headers=get_auth_headers(), timeout=endpoint_timeout)

    if response.status_code != 200:
        logger.error(f'Error while getting problem configuration: {response.text}')
        return False
        # print(f'Error while getting problem configuration: {response.text}')

    try:
        problem_config = response.json()

        problem_config_path = f'problems/{problem_id}'
        if not os.path.exists(problem_config_path):
            os.mkdir(problem_config_path)

        # In this variable are saved the info about each test case,
        # to be retrieved during the judging process
        test_cases = {}
        for test_case_info in problem_config['test_cases']:
            in_file_name = f'{test_case_info["number"]}.in'
            out_file_name = f'{test_case_info["number"]}.out'

            # Write the input test cases
            with open(f'{problem_config_path}/{in_file_name}', 'w') as input_file:
                input_file.write(test_case_info['input'])

            # Write the output test cases
            with open(f'{problem_config_path}/{out_file_name}', 'w') as output_file:
                output_file.write(test_case_info['output'])

            test_cases[test_case_info['number']] = {
                'in': in_file_name,
                'out': out_file_name,
                'number': test_case_info['number'],
                'points': test_case_info['points'],
                'is_pretest': test_case_info['is_pretest'],
            }

        with open(f'{problem_config_path}/config.yml', 'w') as config_file:
            data = { 
                'version': problem_config['config_version_number'], 
                'languages': problem_config['constraints'],
                'test_cases_number': len(problem_config['test_cases']),
                'test_cases': test_cases,
            }
            config_file.write(yaml.dump(data))

        # Multiple files are written:
        # - a configuration file, which includes the info about the problem and
        #   its test cases;
        # - 2 files for each test case: one for the inputs and one for the outputs

    except Exception as e:
        logger.error(f'Error while deserializing server response: {e}')
        # print(f'Error while deserializing server response: {e}')
        return False

    return True


def check_config_version():
    try:
        response = requests.get(config['config_check_api'], headers=get_auth_headers(), timeout=endpoint_timeout)

    except Exception as ex:
        logger.error(f'Error while getting the problems: {ex}')
        # print(f'Error while getting the problems: {ex}')
        return

    if response.status_code != 200:
        logger.error(f'Error while getting problem versions: {response.text}')
        # print(f'Error whi le getting problem versions: {response.text}')
        return
    
    try:
        # response body:
        # { "problem_id": version, "problem_id": version, ... }
        server_versions = response.json()
        for problem_id in server_versions:
            if problem_id not in problem_versions or problem_versions[problem_id] != server_versions[problem_id]:
                success = update_problem_config(problem_id)
                if success: 
                    problem_versions[problem_id] = server_versions[problem_id]

    except Exception as e:
        logger.error(f'Error while deserializing server response: {e}')
        # print(f'Error while deserializing server response: {e}')
        return