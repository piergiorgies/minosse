from pydantic import BaseModel

class Config(BaseModel):
    name: str
    key: str
    problems_path: str
    
    api_url: str
    config_check_api_path: str
    get_problem_config_api_path: str
    send_submission_result_api_path: str
    send_total_submission_result_api_path: str

    rabbitmq_host: str
    rabbitmq_user: str
    rabbitmq_pass: str
    execution_path: str
    execution_user: str

    available_languages: list[str]

    loki_url: str
    log_level: str
    console_log: bool