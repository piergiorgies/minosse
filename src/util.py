from src.config_loader import load_config
import hashlib
config = load_config()

def get_auth_headers():
    name = config['name']
    key = config['key']
    hashed = hashlib.sha256(f'{name}:{key}'.encode()).hexdigest()
    #return the hash as a header
    return {
        'Authorization': f'Bearer {name}:{hashed}'
    }