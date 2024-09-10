import subprocess
import resource
import os
import time
import yaml
import threading
import psutil

from config_loader import load_config 

config = load_config()

def compile_program(compile_command, source_file, executable):
    EXECUTION_PATH = config["execution_path"]
    compile_cmd = compile_command.format(source_file=source_file, executable=executable)            
    # compile_cmd = compilbodye_command.format(source_file=source_file, executable=executable_name)            
    compile_process = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True, cwd=EXECUTION_PATH)
    if compile_process.returncode != 0:
        return {
            'stdout': '',
            'stderr': compile_process.stderr,
            'execution_time': 0,
            'memory_usage': 0,
            'error': 'Compilation failed'
        }
    
    return 0


def execute_code_locally(code, problem_id, language):
    problem_config_file = f'problems/{problem_id}/config.yml'
    if not os.path.exists(problem_config_file):
        raise ValueError(f"Unsupported problem_id: {problem_id}")

    if language not in config['languages']:
        raise ValueError(f"Unsupported language: {language}")

    problem_config_file = open(problem_config_file)
    problem_config = yaml.safe_load(problem_config_file.read())
    if language not in problem_config['languages']:
        raise ValueError(f"Unsupported language: {language}")

    # Check the config for program_id
    # Maybe you can do only one check and save if it is good or bad    

    lang_config = config['languages'][language]
    extension = lang_config['extension']
    compile_command = lang_config.get('compile_command')
    run_command = lang_config['run_command']

    source_filename = lang_config.get('source_filename')
    source_filename = f'{source_filename if source_filename else 'code'}{extension}'

    EXECUTION_PATH = config["execution_path"]

    # Create a temporary file for the code
    # source_file = f'{EXECUTION_PATH}/code{extension}'
    source_file = f'{EXECUTION_PATH}/{source_filename}'
    with open(source_file, 'w') as f:
        f.write(code)
    
    executable = source_file.replace(extension, '')
    executable_name = executable.split('/').pop()
    
    time_limit_ms = problem_config['languages'][language]['time_limit']
    memory_limit_mb = problem_config['languages'][language]['memory_limit']

    max_memory = [0]
    def monitor_memory(proc, max_memory):
        try:
            while proc.is_running():
                memory_info = proc.memory_info()
                max_memory[0] = max(max_memory[0], memory_info.rss)
                # time.sleep(0.01)  # Adjust as needed for precision
        except psutil.NoSuchProcess:
            pass

    results = []
    total_points = 0
    try:
        # Compile the code if necessary
        if compile_command:
            compilation_result = compile_program(compile_command, source_file, executable)
            # If compilation result isn't zero, is an object which report
            # the compilation errors...
            if compilation_result != 0:
                return compilation_result


        # Set resource limits
        def set_limits():
            # Set maximum CPU time in seconds
            resource.setrlimit(resource.RLIMIT_CPU, (time_limit_ms, time_limit_ms))
            # Set maximum memory usage in bytes
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit_mb * 1024 * 1024, memory_limit_mb * 1024 * 1024))

        # Run the code with input
        run_cmd = run_command.format(source_file=source_file, executable=executable_name)

        for case_config in problem_config['test_cases']:
            # case_config = problem_config['test_cases'][test_case['name']]
            inputs = open(f'problems/{problem_id}/{case_config["in"]}').read()
            outputs = open(f'problems/{problem_id}/{case_config["out"]}').read()

            start_time = time.time()
            process = subprocess.Popen(
                run_cmd, 
                preexec_fn=set_limits,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                cwd=EXECUTION_PATH,
            )
            
            ps_process = psutil.Process(process.pid)
            memory_thread = threading.Thread(target=monitor_memory, args=(ps_process, max_memory,))
            memory_thread.start()

            try:
                stdout, stderr = process.communicate(input=inputs, timeout=time_limit_ms)
                end_time = time.time()
                execution_time = end_time - start_time

                error = 'Wrong answer'
                if stdout.strip() == outputs:
                    error = None
                    total_points += case_config['points']

                results.append({
                    'stdout': stdout,
                    'stderr': stderr,
                    'execution_time': execution_time,
                    'memory_usage': max_memory[0] / 1024,
                    'error': error,
                })
            except subprocess.TimeoutExpired:
                process.kill()
                results.append({
                    'stdout': '',
                    'stderr': 'Process exceeded time limit.',
                    'execution_time': time_limit_ms,
                    'memory_usage': max_memory[0] / 1024,
                    'error': 'Timeout'
                })

    finally:
        # Cleanup: Remove the temporary source file
        if os.path.exists(source_file):
            os.remove(source_file)

    return {
        'total_points': total_points,
        'results': results,
    }

    
