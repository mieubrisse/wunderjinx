import utils as wj_utils
import yaml
import os.path

script_dir = os.path.dirname(os.path.realpath(__file__))

# TODO Let user set the config path as they please!
config_filepath = os.path.join(script_dir, "config.yaml")
with open(config_filepath) as config_fp:
    _config_obj = yaml.load(config_fp)

CLIENT_ID =  _config_obj["client_id"]
ACCESS_TOKEN = _config_obj["access_token"]
QUEUE = _config_obj["queue"]
RABBITMQ_HOST = _config_obj["rabbitmq_host"]
DATETIME_FORMAT = _config_obj["datetime_format"]

# TODO Temporary until list_resolver is ipmlemented
DEFAULT_LIST_ID = _config_obj["default_list_id"]
