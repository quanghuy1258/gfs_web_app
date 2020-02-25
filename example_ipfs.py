#!/usr/bin/python3

import json, random

# IPFS HTTP Client Library
import ipfshttpclient

file_path = "example_important.txt"

class IpfsMaster():
  ADDRESS_BASE = '/ip4/{0}/tcp/{1}/http'

  def __init__(self, config_path):
    self.__config = []
    config = None
    with open(config_path, 'r') as f:
      config = json.load(f)
    if type(config) is not list:
      return
    for node in config:
      if (type(node) is not dict) or ('ip' not in node) or ('port' not in node):
        continue
      self.__config.append({'ip': node['ip'], 'port': node['port']})

  def getClient(self):
    if len(self.__config) < 1:
      return None
    rand = random.randrange(len(self.__config))
    client = None
    for i in range(len(self.__config)):
      node = self.__config[(rand + i) % len(self.__config)]
      try:
        ip = node['ip']
        port = node['port']
        client = ipfshttpclient.connect(self.ADDRESS_BASE.format(ip, port))
        break
      except:
        client = None
        continue
    return client

# Upload file
ipfs_master = IpfsMaster("example.conf")
client = ipfs_master.getClient()
info = client.add(file_path)
result = client.object.patch.add_link(info['Hash'], info['Name'], info['Hash'])
hash_str = result['Hash']
client.close()

# Debug information
print("hash_bin = {}".format(hash_str))
client = ipfs_master.getClient()
obj_links = client.object.links(hash_str)
print("name_str = {}".format(obj_links['Links'][0]['Name']))
print("hash_str = {}".format(obj_links['Links'][0]['Hash']))
client.get(hash_str)
client.close()
