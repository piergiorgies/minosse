import yaml

from src.models.config import Config

config = None
def load_config(file_path='config.yml') -> Config:
    global config

    if config == None:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            config = Config(**config)
    
    return config