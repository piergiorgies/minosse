import requests
import os
import yaml

from config_loader import load_config

config = load_config()
problem_versions = {}

def update_problem_config(problem_id):
    api_url = config['get_problem_config_api']
    api_url = api_url.format(problem_id=problem_id)

    # Credentials to authenticate to the server
    # We need them to prvent user accessing the test case instances
    body = { 'name': config['name'], 'key': config['key'] }
    response = requests.post(api_url, json=body)

    if response.status_code != 200:
        print(f'Error while getting problem configuration: {response.text}')

    try:
        # response body:
        # { 
        #   "problem_id": id, 
        #   "problem_version": version,
        #   "languages": {
        #       "language_id": {
        #           "memory_limit": ...,
        #           "time_limit": ...
        #       },
        #       ...
        #   }
        #   "test_cases": [
        #       { 
        #           "name": case_name, 
        #           "number": case_number, 
        #           "points": case_points,
        #           "is_pretest": True/False
        #           "input": ..., 
        #           "output": ... 
        #       },
        #       ...
        #   ] 
        # }
        problem_config = response.json()

        problem_config_path = f'problems/{problem_id}'
        if not os.path.exists(problem_config_path):
            os.mkdir(problem_config_path)

        # In this variable are saved the info about each test case,
        # to be retrieved during the judging process
        test_cases = {}
        for test_case_info in problem_config['test_cases']:
            in_file_name = f'{test_case_info["case_name"]}.in'
            out_file_name = f'{test_case_info["case_name"]}.out'

            # Write the input test cases
            with open(f'{problem_config_path}/{in_file_name}', 'w') as input_file:
                input_file.write(test_case_info['input'])

            # Write the output test cases
            with open(f'{problem_config_path}/{out_file_name}', 'w') as output_file:
                output_file.write(test_case_info['output'])

            test_cases[test_case_info['case_name']] = {
                'in': in_file_name,
                'out': out_file_name,
                'number': test_case_info['number'],
                'points': test_case_info['points'],
                'is_pretest': test_case_info['is_pretest'],
            }

        with open(f'{problem_config_path}/config.yml', 'w') as config_file:
            data = { 
                'version': problem_config['problem_version'], 
                'languages': problem_config['languages'],
                'test_cases_number': len(problem_config['test_cases']),
                'test_cases': test_cases,
            }
            config_file.write(yaml.dump(data))

        # Multiple files are written:
        # - a configuration file, which includes the info about the problem and
        #   its test cases;
        # - 2 files for each test case: one for the inputs and one for the outputs

    except Exception as e:
        print(f'Error while deserializing server response: {e}')


def check_config_version():
    response = requests.get(config['config_check_api'])

    if response.status_code != 200:
        print(f'Error while getting problem versions: {response.text}')
        return
    
    try:
        # response body:
        # { "problem_id": version, "problem_id": version, ... }
        server_versions = response.json()
        for problem_id in server_versions:
            if problem_id not in problem_versions or problem_versions[problem_id] != server_versions[problem_id]:
                update_problem_config(problem_id)
                problem_versions[problem_id] = server_versions[problem_id]

    except Exception as e:
        print(f'Error while deserializing server response: {e}')
        return