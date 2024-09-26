# ByteBlitz judge

## Running the judge
1. Create the settings file
`cp config_example.yml config.yml`
and edit the parameters with the right values. [Here](#configuration-parameters) there's a description of each parameter.
2. Build the docker image with
`docker build -t byteblitz/minosse .`
3. Run the service with
`docker compose up`
  
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

### RabbitMQ parameters

### Execution parameters