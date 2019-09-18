#!/usr/bin/python3
import logging
import time
from enum import Enum

import ipfshttpclient

from helpers.config_helper import config_helper

log = logging.getLogger('ipfs_connector.ipfs_connector')
log.setLevel(logging.DEBUG)

ADDRESS_BASE = "/ip4/{0}/tcp/{1}/http"


class State(Enum):
    CONNETED = 1
    DISCONNECTED = 0


configuration = config_helper("")


class ipfs_connector(object):
    """
    Connector for listening and connecting to IPFS hosts
    """

    def __init__(self, ipfs_server=None, ipfs_port=None):
        self.ipfs = None
        self.ipfs_server = ipfs_server
        self.ipfs_port = ipfs_port
        self.queue = None
        self.backlog = []
        self.state = State.DISCONNECTED

    def connect(self):
        ipfs_retries = 5
        ipfs_retry_count = 0
        while self.ipfs is None:
            try:
                host = self._random_select()
                self.ipfs_server = host.hostname
                self.ipfs_port = host.port
                self.ipfs = ipfshttpclient.connect(
                    ADDRESS_BASE.format(self.ipfs_server, self.ipfs_port)
                )
                self.state = State.CONNETED
            except ipfshttpclient.exceptions.ConnectionError as e:
                log.exception("Retried connection {} times.".format(ipfs_retries))
                raise e
            else:
                log.debug("Connecting to IPFS - Error. Retrying in 0.5s...")

            time.sleep(0.5)
            ipfs_retry_count += 1

    def disconnect(self, abort=False):
        """
        Disconnect from the server.
        :param abort: If set "True", do not wait for background
        """
        if self.state == State.CONNETED and self.ipfs is not None:
            self.ipfs.stop()
            self.state = State.DISCONNECTED

    @staticmethod
    def _random_select():
        import random
        return random.choice(configuration.ipfs_hosts)


if __name__ == "__main__":
    connector = ipfs_connector()
    connector.connect()
    print(connector.ipfs.id())
