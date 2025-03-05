from src.config_loader import load_config
import hashlib
import time
import requests

config = load_config()

def get_auth_headers():
    name = config['name']
    key = config['key']
    hashed = hashlib.sha256(f'{name}:{key}'.encode()).hexdigest()
    #return the hash as a header
    return {
        'Authorization': f'Bearer {name}:{hashed}'
    }

def send_partial_result(submission_id, data_to_send):
    sent = False
    api_url = config['send_submission_result_api']
    api_url = api_url.format(submission_id=submission_id)
    for _ in range(3):
        try:
            response = requests.post(api_url, json=data_to_send, headers=get_auth_headers())
            if response.status_code != 200:
                time.sleep(0.2)
            else:
                sent = True
                break
        except Exception:
            pass

    if not sent:
        print(f'Failed in sending submission {submission_id}')