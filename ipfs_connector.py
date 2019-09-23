#!/usr/bin/python3
import logging
import time
from enum import Enum
import ipfshttpclient
from ipfshttpclient import Client

from helpers.config_helper import config_helper, DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_PATH

log = logging.getLogger('ipfs_connector.ipfs_connector')
log.setLevel(logging.DEBUG)

ADDRESS_BASE = "/ip4/{0}/tcp/{1}/http"


class State(Enum):
    CONNETED = 1
    DISCONNECTED = 0


configuration = config_helper()


class ipfs_connector(object):
    """
    Connector for listening and connecting to IPFS hosts
    :param Client ipfs_instance: Ipfs instance node to connect to
    :param str ipfs_server: Ip of host server
    :param int ipfs_port: Port api ipfs of server

    """

    def __init__(self, ipfs_instance=None, ipfs_server=None, ipfs_port=None):
        self.ipfs = ipfs_instance
        self.ipfs_server = ipfs_server
        self.ipfs_port = ipfs_port
        self.queue = None
        self.backlog = []
        self.state = State.DISCONNECTED

    def connect(self):
        """
        Connect to the server from list hosts in config file.

        """
        ipfs_retries = 5
        ipfs_retry_count = 0
        host, hosts_remain = self._random_select(configuration.ipfs_hosts)
        while not self._is_available(self.ipfs):
            try:
                self.ipfs_server = host.hostname
                self.ipfs_port = host.port
                self.ipfs = ipfshttpclient.connect(
                    ADDRESS_BASE.format(self.ipfs_server, self.ipfs_port)
                )
                self.state = State.CONNETED
            except ipfshttpclient.exceptions.ConnectionError as e:
                if ipfs_retry_count >= ipfs_retries or len(hosts_remain) == 0:
                    log.exception("Retried connection {} times.".format(ipfs_retries))
                    raise ValueError("You need to provide other hosts")
                else:
                    log.warning(e)
                    log.debug("Connecting to IPFS - Error. Retrying in 0.5s...")

            time.sleep(0.5)
            ipfs_retry_count += 1
            host, hosts_remain = self._random_select(list_host=configuration.ipfs_hosts,
                                                     shuffle=False)

    def disconnect(self, abort=False):
        """
        Disconnect from the server.
        :param abort: If set "True", do not wait for background

        """
        if self.state == State.CONNETED and self.ipfs is not None:
            self.ipfs.stop()
            self.state = State.DISCONNECTED

    def get_info(self, cid):
        self.ipfs.object.get(cid)

    @staticmethod
    def _random_select(list_host, shuffle=True):
        import random
        _list_host = list_host
        if shuffle:
            random.shuffle(_list_host)
        _first_choice_host = _list_host.pop()
        return _first_choice_host, _list_host

    @staticmethod
    def _is_available(ipfs_instance):
        """
        Return whether the IPFS daemon is reachable or not
        """
        _is_available = False
        if ipfs_instance is None:
            _is_available = False
        else:
            _is_available = True
        return _is_available


if __name__ == "__main__":
    connector = ipfs_connector()
    connector.connect()
    print(connector.ipfs.id())
