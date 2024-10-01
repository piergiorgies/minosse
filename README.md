# ByteBlitz judge

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