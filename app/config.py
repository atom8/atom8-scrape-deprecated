from . import etc


# DEFAULT_SETTINGS_PATH = os.path.join(
#     os.path.dirname(os.path.realpath(__file__)), '../settings.json')

# configuration file
config = None
CONFIG_PATH = 'config.json'


def get_config():
    return config


def load_config():
    global config

    conf_raw = etc.retrieve_JSON(CONFIG_PATH)
    config = Config(conf_raw)

    return config


class Config():

    def __init__(self, config_json):
        self.options = None
        self.options_path = ''

        options_path = config_json.get('options_path')

        try:
            options = etc.retrieve_JSON(options_path)

            self.options = options
            self.options_path = options_path

        except FileNotFoundError:
            print("WARN: Could not load config options. %s" % options_path)

    def save_config(self):
        etc.export_JSON(
            CONFIG_PATH,
            {
                'options_path': self.options_path
            }
        )

    def save_options(self):
        etc.export_JSON(self.options_path, self.options)

    def set_options(self, options_json, options_path):
        self.options = options_json
        self.options_path = options_path
