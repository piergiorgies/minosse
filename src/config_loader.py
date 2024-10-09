import yaml

config = None
def load_config(file_path='config.yml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)