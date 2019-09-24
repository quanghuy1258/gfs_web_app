#!/usr/bin/python3
import unittest
from jsonschema import validate
from helpers.config_helper import config_helper
from tests.default_data import default_data


class Testcases(unittest.TestCase):
    def test_get_hosts_ipfs(self):
        try:
            result = {}
            for i, host in enumerate(config_helper().ipfs_hosts):
                key = "host" + str(i)
                value = host.hostname + ":" + str(host.port)
                result.update({key: value})
            validate(result, default_data.expected_get_hosts)
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
