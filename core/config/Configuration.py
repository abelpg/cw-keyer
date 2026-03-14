import configparser
import logging

class Configuration:

    CONFIG_FILE = "config.ini"

    @staticmethod
    def put_config( section: str, key: str, value: str):
        config = configparser.ConfigParser()
        config.read(Configuration.CONFIG_FILE)

        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, value)

        with open(Configuration.CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def get_config( section: str, key: str, default_value: str = None):
        config = configparser.ConfigParser()
        config.read(Configuration.CONFIG_FILE)
        if config.has_section(section) and config.has_option(section, key):
            return config.get(section, key)
        return default_value

