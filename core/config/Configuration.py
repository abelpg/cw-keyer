import configparser
import logging


class Configuration:

    CONFIG_FILE = "config.ini"

    def __init__(self):
        self._config =  configparser.ConfigParser()
        self._config.read(Configuration.CONFIG_FILE)

    def put_config(self, section: str, key: str, value: str):
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, value)

        with open(Configuration.CONFIG_FILE, 'w') as configfile:
            self._config.write(configfile)

    def get_config(self, section: str, key: str):
        if self._config.has_section(section) and self._config.has_option(section, key):
            return self._config.get(section, key)
        return None

