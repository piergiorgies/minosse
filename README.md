# ByteBlitz judge
The code executor for ByteBlitz™.

## How does it work?
Minosse works together with other two entities: the official ByteBlitz™ backend and a RabbitMQ server.
The software functions as a distributed judge system that automates the execution of code submissions; more istances (every one with a unique name) can be run at the same time (the load balance is manage by RabbitMQ). Below is a high-level overview of the process:
1. Submission of code: the judges receive code submissions through a RabbitMQ server. RabbitMQ acts as a broker that ensures efficient, asynchronous, and reliable communication between the server and the worker nodes (judges).
2. Upon receiving a submission, a worker node will extract the code and any required execution details, execute the code in a controlled environment and monitor the execution for time limits and memory usage.
3. After the execution completes, the worker node compiles the results. The results are then sent back to the server through a web API.

The results of the submission are sent back with different messages: one for each test case and one cumulative, which is a summary of the previous ones. The format of the messages are described next.

### Single case message
```json
{
    "number": "<test_case_number>",
    "note": "Compilation/execution errors",
    "memory": "<memory_usage>",
    "time": "<execution_time>",
    "result_id": "<result_id>"
}
```

### Submission summary
```json
{
    "result_id": "<result_id>"
}
```

## Running the judge
This section is intended for the users who only want to deploy a production instance. If you want to run for debugging purposes see [the developer section](#running-the-judge-developers).

1. Create the settings file
    ```shell
    cp config_example.yml config.yml
    ```
    and edit the parameters with the right values. [Here](#configuration-parameters) there's a description of each parameter.
2. Build the docker image with
    ```shell
    docker build -t byteblitz/minosse .
    ```
3. Run the service with
    ```shell
    docker compose up
    ```
  
  The default configuration will also start a RabbitMQ instance, to which the judge will connect. If you want to start only the judge, comment or remove the RabbitMQ service definition in the `docker-compose.yml`:
```yml
services:
# The commented part could be deleted (if you don't need RabbitMQ)
#   rabbitmq:
#       image: rabbitmq:management
#       container_name: rabbitmq
#       environment:
#           - RABBITMQ_DEFAULT_USER=apo
#           - RABBITMQ_DEFAULT_PASS=ApoChair2023!
#       ports:
#           - "5672:5672"
#           - "15672:15672" 
    minosse:
        container_name: minosse
        cap_add:
            - NET_ADMIN
            - NET_RAW
        image: byteblitz/minosse
        command: /app/venv/bin/python -u /app/main.py

networks:
    default:
        driver: bridge
```
and set the right rabbitmq connection values in the `config.yml` file **before building the image**.

## Configuration parameters

### Judge parameters
`name` 
> The name of the judge instance. It must be unique in case you are running multiple judges with the same backend.

`key`
>  The secret key to use to authenticate to the API server.

`problems_path`
> The path where the data related to the problems and test cases will be saved

**Notes**: the `name` and the `key` parameters are _authentication_ parameter; this means that they must be specified on the server first (see _link to site docs where it is explained how to add a judge_).

### Server API parameters
`config_check_api`
> The url that the judge will use to get the problem list with their configuration id.

`get_problem_config_api`
> The url that the judge will use to download the details of one specific problem (with its test cases). To specify where the id of the specific problem must be placed, you must use the wildcard `{problem_id}` (example: `https://domain/problems/{problem_id}`).

`send_submission_result_api`
> The url that the judge will use to send the result of the execution of a single test case. To specify where the id of the specific submission must be placed, you must use the wildcard `{submission_id}` (example: `https://domain/submissions/{submission_id}`).

`send_total_submission_result_api`
> The url that the judge will use to send the result of the execution of all test cases (aggregated info). To specify where the id of the specific submission must be placed, you must use the wildcard `{submission_id}` (example: `https://domain/submissions/{submission_id}`).

### RabbitMQ parameters
`rabbitmq_host`
> Hostname of the RabbitMQ server.

`rabbitmq_user`
> Username to use to be authenticated by the RabbitMQ server.

`rabbitmq_pass`
> Password to use to be authenticated by the RabbitMQ server.

### Execution parameters
`execution_path`
> The path where the source code will be moved, eventually compiled and executed.

`languages`
> The list of the languages supported by the judge. Each language must be uniquely defined in the file with an id and must specify some parameters; those parameters are based on the language defined.

`languages.id.extension`
> The extension of the file to save.

`languages.id.run_command`
> The command to run and valuate the program.

`languages.id.compile_command`
> The command to run to compile the program. This must be specified only with compiled languages, like C, C++, Rust, etc...

`languages.id.source_filename`
> The filename to give to the source file. This is useful for some languages (like Java, which needs that the file to execute must be named 'Main.java').

## Running the judge (developers)
**Dependencies:** python (version >= 3.7) and pip.
1. Create a python virtual environment
    ```shell
    python -m venv <venv_name>
    ```
2. Activate the previously created virtual environment
    _Linux and MacOS:_
    ```shell
    source <venv_name>/bin/activate
    ```
    _Windows (powershell):_
    ```shell
    <venv_name>\Scripts\Activate.ps1
    ```
3. Install the required python dependencies
    ```shell
    pip install -r requirements.txt
    ```
4. Execute the judge
    ```shell
    python main.py
    ```

**Notes:** when you're done, you can deactivate the virtual environment with
```shell
deactivate
```
The commands will run only the judge istance. The ByteBlitz backend and the RabbitMQ server aren't included.