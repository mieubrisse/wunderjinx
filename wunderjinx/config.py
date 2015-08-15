import utils as wj_utils
import yaml

# TODO Let user set the config path as they please!
with open("config.yaml") as config_fp:
    _config_obj = yaml.load(config_fp)

CLIENT_ID =  _config_obj["client_id"]
ACCESS_TOKEN = _config_obj["access_token"],
QUEUE = _config_obj["queue"],
RABBITMQ_HOST = _config_obj["rabbitmq_host"],
DATETIME_FORMAT = _config_obj["datetime_format"]
