#!/usr/bin/python3
import logging
import os
from configparser import ConfigParser
from urllib.parse import urlparse

log = logging.getLogger('helpers.config_helper')
log.setLevel(logging.DEBUG)

DEFAULT_CONFIG_FILENAME = "config.ini"
DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))
DEFAULT_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))


class config_helper(object):
    """
        Helper for configuration file
    """

    def __init__(self, conf_path=None):
        self.ipfs_hosts = []
        self.bwf_hosts = []
        # Get file config from abspath
        if not conf_path or not os.path.exists(os.path.abspath(conf_path)):
            conf_file = DEFAULT_CONFIG_FILE
            log.debug("[{0}] does not exist, the following path will "
                      "be used:\n[{1}]".format(os.path.abspath(conf_file), conf_file))
        else:
            conf_file = conf_path + DEFAULT_CONFIG_FILENAME

        # Read and parse config file with ConfigParser
        configparser = ConfigParser()
        configparser.read(conf_file)

        # Get list hosts of Blockchain and IPFS
        self.bwf_hosts = self._get_hosts(configparser["BEOWULF"]["bwf_hosts"])
        self.ipfs_hosts = self._get_hosts(configparser["IPFS"]["ipfs_hosts"])

    @staticmethod
    def _get_hosts(config_value):
        hosts = []
        try:
            urls = [host.strip(' -')
                    for host in config_value.strip().split('\n')]

            for url in urls:
                host = urlparse(url)
                if host.scheme in ["http", "https"]:
                    # print(host.hostname, host.port)
                    hosts.append(host)
                else:
                    log.debug("Cannot parse url: [{}]".format(url))
        except Exception as e:
            log.exception("Cannot get url from config file")
            raise e

        return hosts

