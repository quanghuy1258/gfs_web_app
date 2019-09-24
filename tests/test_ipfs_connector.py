#!/usr/bin/python3
import os
import unittest
from ipfs_connector import ipfs_connector, State

connector = ipfs_connector()


class Testcases(unittest.TestCase):
    def test_connect(self):
        try:
            connector.connect()
            assert connector.state == State.CONNETED
        except Exception as e:
            self.fail(e)

    def test_disconnect(self):
        try:
            connector.disconnect()
            assert connector.state == State.DISCONNECTED
        except Exception as e:
            self.fail(e)

    def test_add_info(self):
        try:
            connector.connect()
            from helpers.config_helper import DEFAULT_CONFIG_FILE
            result = connector.ipfs.add(DEFAULT_CONFIG_FILE)
            new_hash = connector.add_info_to_object(result)
            assert new_hash == "QmRBn7HHydU98tgGBDAwasAG3MVsaMk28Lwq7oRj8bQkBj"
        except Exception as e:
            self.fail(e)

    def test_get_info(self):
        try:
            connector.connect()
            hash_object_info = "QmRBn7HHydU98tgGBDAwasAG3MVsaMk28Lwq7oRj8bQkBj"
            result = connector.get_info_from_linked_object(hash_object_info)
            assert result['Hash'] == "QmPfLdy12fEzrAaBf1EDFvPV9wkLLsub3tyAQLqZMXPR2V"
            assert result['Size'] == 287
            assert result['Name'] == "config.ini"
        except Exception as e:
            self.fail(e)

    def test_get_file_from_new_hash(self):
        try:
            connector.connect()
            hash_object_info = "QmRBn7HHydU98tgGBDAwasAG3MVsaMk28Lwq7oRj8bQkBj"
            connector.ipfs.get(hash_object_info)
            assert hash_object_info in os.listdir(os.getcwd())
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()