import logging
import time
from enum import Enum

import ipfshttpclient

log = logging.getLogger('ipfs_connector.ipfs_connector')
log.setLevel(logging.DEBUG)

ADDRESS_BASE = "/ip4/{0}/tcp/{1}/http"


class State(Enum):
    CONNETED = 1
    DISCONNECTED = 0

connected_clients = []


class ipfs_connector(object):
    """
    Listen and connect to IPFS hosts
    """

    def __init__(self, ipfs_server, ipfs_port):
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
                self.ipfs = ipfshttpclient.connect(
                    ADDRESS_BASE.format(self.ipfs_server, self.ipfs_port)
                )
                self.state = State.CONNETED
                connected_clients.append(self)
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
            try:
                connected_clients.remove(self)
            except ValueError:
                pass
