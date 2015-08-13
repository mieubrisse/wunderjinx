import utils as wj_utils
import yaml

ConfigKeys = wj_utils.enum(
    CLIENT_ID =  "client_id",
    ACCESS_TOKEN = "access_token",
    QUEUE = "queue",
    RABBITMQ_HOST = "rabbitmq_host",
)

def _validate_config(config):
    # TODO We'll probably need to adjust this as we add non-required variables
    for enum_key, enum_val in ConfigKeys.iteritems():
        if enum_val not in config:
            raise ValueError("Error: Missing config parameter '{}'".format(enum_val))
        config_val = config[enum_val]
        if not config_val or len(config_val.strip()) == 0:
            raise ValueError("Error: Empty value for config parameter '{}'".format(enum_val))

def load_config(config_filepath):
    with open(config_filepath) as config_fp:
        config = yaml.load(config_fp)
        _validate_config(config)
        return config
