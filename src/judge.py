import subprocess
import resource
import os
import time
import yaml
import threading
import psutil
import tempfile

from src.config_loader import load_config 
from src.models.errors import EXECUTION_RESULTS, CompilationError
from src.util import send_partial_result
from src.models.submission_dto import SubmissionDTO
from src.models.problem_info_dto import ProblemConfig
from src.languages.base_language import BaseLanguage
from src.languages.c import C

from src.isolate import isolate_init, isolate_run, isolate_cleanup

config = load_config()

def compile_program(compile_command, source_file, executable):
    EXECUTION_PATH = config["execution_path"]
    compile_cmd = compile_command.format(source_file=source_file, executable=executable)         
    compile_process = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True, cwd=EXECUTION_PATH)
    if compile_process.returncode != 0:
        raise CompilationError(compile_process.stderr)
    
    return 0

commands_managers: dict[str, BaseLanguage] = {
    'C': C()
}

def execute_code_locally(submission_dto: SubmissionDTO):
    problem_config_file = f'problems/{submission_dto.problem_id}/config.yml'
    if not os.path.exists(problem_config_file):
        raise ValueError(f"Unsupported problem_id: {submission_dto.problem_id}")

    problem_config_file = open(problem_config_file)
    problem_config = yaml.safe_load(problem_config_file.read())
    problem_config = ProblemConfig(**problem_config)

    # Check the config for program_id
    # Maybe you can do only one check and save if it is good or bad
    lang_config = next(c for c in problem_config.constraints if c.language_name == submission_dto.language)
    if lang_config == None or submission_dto.language not in commands_managers:
        raise ValueError(f"Unsupported language: {submission_dto.language}")

    file_extension = commands_managers[submission_dto.language].get_file_extension()
    source_name = 'problem'
    source_complete_name = f'{source_name}{file_extension}'
    
    box_id = submission_dto.submission_id
    box_path = isolate_init(box_id)
    file_path = f'{box_path}/box/{source_complete_name}'
    with open(file_path, 'x') as source_file:
        source_file.write(submission_dto.code)

    compile_cmd = commands_managers[submission_dto.language].get_compile_commands(source_complete_name, source_name)
    return_code = isolate_run(compile_cmd, box_id, box_path)
    print(return_code)

    # isolate_cleanup(box_id)

# def execute_code_locally(code, problem_id, language, submission_id, is_pretest_run):
#     problem_config_file = f'problems/{problem_id}/config.yml'
#     if not os.path.exists(problem_config_file):
#         raise ValueError(f"Unsupported problem_id: {problem_id}")

#     if language not in config['languages']:
#         raise ValueError(f"Unsupported language: {language}")

#     problem_config_file = open(problem_config_file)
#     problem_config = yaml.safe_load(problem_config_file.read())
#     # languages_names = list(map(lambda x: x['language_id'], problem_config['languages']))
#     # if language not in languages_names:
#     #     raise ValueError(f"Unsupported language: {language}")

#     # Check the config for program_id
#     # Maybe you can do only one check and save if it is good or bad

#     lang_config = config['languages'][language]
#     extension = lang_config['extension']
#     compile_command = lang_config.get('compile_command')
#     run_command = lang_config['run_command']

#     source_filename = lang_config.get('source_filename')
#     source_filename = f'{source_filename if source_filename else 'code'}{extension}'

#     EXECUTION_PATH = config["execution_path"]
#     EXECUTION_USER = config["execution_user"]

#     # Create a temporary file for the code
#     source_file = f'{EXECUTION_PATH}/{source_filename}'
#     with open(source_file, 'w') as f:
#         f.write(code)
    
#     executable = source_file.replace(extension, '')
#     executable_name = executable.split('/').pop()
    
#     problem_language_config = [l for l in problem_config['languages'] if l['language_name'] == language][0]

#     time_limit_ms = problem_language_config['time_limit']
#     memory_limit_mb = problem_language_config['memory_limit']

#     max_memory = [0]
#     def monitor_memory(proc, max_memory):
#         try:
#             while proc.is_running():
#                 memory_info = proc.memory_info()
#                 max_memory[0] = max(max_memory[0], memory_info.rss)
#                 # time.sleep(0.01)  # Adjust as needed for precision
#         except psutil.NoSuchProcess:
#             pass

#     results = []
#     total_points = 0
#     try:
#         # Compile the code if necessary
#         if compile_command:
#             try:
#                 compile_program(compile_command, source_file, executable)
#             except CompilationError as e:
#                 raise e

#         # Set resource limits
#         def set_limits():
#             # Set maximum CPU time in seconds
#             resource.setrlimit(resource.RLIMIT_CPU, (time_limit_ms, time_limit_ms))
#             # Set maximum memory usage in bytes
#             resource.setrlimit(resource.RLIMIT_AS, (memory_limit_mb * 1024 * 1024, memory_limit_mb * 1024 * 1024))

#         # Run the code with input
#         run_cmd = run_command.format(source_file=source_file, executable=executable_name)

#         # Run the code for each test case (if is_pretest_run is True, only run pretest cases)
#         test_cases = []
#         if is_pretest_run:
#             for case in problem_config['test_cases']:
#                 if problem_config['test_cases'][case]['is_pretest']:
#                     test_cases.append(case)
#         else:
#             test_cases = problem_config['test_cases']

#         for case_config in test_cases:
#             number = case_config
#             case_config = problem_config['test_cases'][number]
#             inputs = open(f'problems/{problem_id}/{case_config["in"]}').read()
#             outputs = open(f'problems/{problem_id}/{case_config["out"]}').read()

#             start_time = time.time()
#             process = subprocess.Popen(
#                 run_cmd, 
#                 preexec_fn=set_limits,
#                 stdin=subprocess.PIPE,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True,
#                 shell=True,
#                 cwd=EXECUTION_PATH,
#                 user=EXECUTION_USER
#             )
            
#             ps_process = psutil.Process(process.pid)
#             memory_thread = threading.Thread(target=monitor_memory, args=(ps_process, max_memory,))
#             memory_thread.start()

#             execution_result = None
#             try:
#                 stdout, stderr = process.communicate(input=inputs, timeout=time_limit_ms / 1000)
#                 end_time = time.time()
#                 execution_time = end_time - start_time

#                 # error = 'Wrong answer'
#                 error = EXECUTION_RESULTS['WRONG_ANSWER']
#                 if stdout.strip() == outputs:
#                     # error = None
#                     error = EXECUTION_RESULTS['ACCEPTED']
#                     total_points += case_config['points']

#                 execution_result = {
#                     'stdout': stdout,
#                     'stderr': stderr,
#                     'execution_time': execution_time,
#                     'memory_usage': max_memory[0] / 1024,
#                     'result_id': error,
#                 }
#                 results.append(execution_result)
#             except subprocess.TimeoutExpired:
#                 process.kill()
#                 execution_result = {
#                     'stdout': '',
#                     'stderr': 'Process exceeded time limit.',
#                     'execution_time': time_limit_ms / 1000,
#                     'memory_usage': max_memory[0] / 1024,
#                     'result_id': EXECUTION_RESULTS['TIME_LIMIT']
#                 }
#                 results.append(execution_result)

#             data_to_send = {
#                 'number': number,
#                 'notes': execution_result['stderr'],
#                 'memory': execution_result['memory_usage'],
#                 'time': execution_result['execution_time'],
#                 'result_id': execution_result['result_id'],
#                 'is_pretest_run': is_pretest_run,
#                 'output': execution_result['stdout'] if is_pretest_run else None,
#             }

#             send_partial_result(submission_id, data_to_send)

#     finally:
#         # Cleanup: Remove the temporary source file
#         if os.path.exists(source_file):
#             os.remove(source_file)

#     return {
#         'total_points': total_points,
#         'results': results,
#     }

    
