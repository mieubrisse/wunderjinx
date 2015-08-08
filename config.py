import yaml

class ConfigKeys:
    client_id = "client_id"
    access_token = "access_token"

def load_config(config_filepath):
    with open(config_filepath) as config_fp:
        return yaml.load(config_fp)
