#!/usr/bin/python3

import json, random, base64

# Cryptography Library
from cryptography.fernet import Fernet

# BEOWULF Library
from beowulf.beowulfd import Beowulfd
from beowulf.commit import Commit
from beowulf.account import Account
from beowulfbase import memo, account

# IPFS HTTP Client Library
import ipfshttpclient

# beowulfd_instance
s = Beowulfd()

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
    ip = None
    port = None
    client = None
    for i in range(len(self.__config)):
      node = self.__config[(rand + i) % len(self.__config)]
      try:
        ip = node['ip']
        port = node['port']
        client = ipfshttpclient.connect(self.ADDRESS_BASE.format(ip, port))
        break
      except:
        ip = None
        port = None
        client = None
        continue
    return client, ip, port

class UploadFile():
  def __encrypt_file(self, file_path):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    with open(file_path, 'rb') as file_obj:
      with open(file_path + '.enc', 'wb') as file_enc_obj:
        file_enc_obj.write(base64.urlsafe_b64decode(fernet.encrypt(file_obj.read())))
    return key.decode()

  def __upload_file(self, ipfs_master, file_path):
    client, ip, port = ipfs_master.getClient()
    hash_str = client.add(file_path)['Hash']
    client.close()
    return hash_str, ip, port

  def __create_memo(self, key, hash_str, ip, port):
    memo_str = json.dumps({'key': key, 'hash': hash_str, 'ip': ip, 'port': port})
    return memo_str

  def __make_tx(self, pri_key_str, pub_key_str, memo_str):
    c = Commit(beowulfd_instance=s, keys = [pri_key_str])
    from_acc = c.wallet.getAccountFromPrivateKey(pri_key_str)
    to_acc = c.wallet.getAccountFromPublicKey(pub_key_str)
    txid = c.transfer(account=from_acc, to=to_acc, amount='0.01', asset='W', fee='0.01', asset_fee='W', memo='#' + memo_str)['id']
    return txid

  def __init__(self, file_path, ipfs_master, pri_key_sender, pub_key_receiver):
    key = self.__encrypt_file(file_path)
    hash_str, ip, port = self.__upload_file(ipfs_master, file_path)
    memo_str = self.__create_memo(key, hash_str, ip, port)
    self.__txid = self.__make_tx(pri_key_sender, pub_key_receiver, memo_str)

  def get_txid(self):
    return self.__txid

class DownloadFile():
  def __decrypt_file(self, key, file_enc_name):
    fernet = Fernet(key.encode())
    with open(file_enc_name, 'rb') as file_enc_obj:
      with open(file_enc_name + '.dec', 'wb') as file_obj:
        file_obj.write(fernet.decrypt(base64.urlsafe_b64encode(file_enc_obj.read())))

  def __download_file(self, hash_str, ip, port):
    try:
      client = ipfshttpclient.connect(IpfsMaster.ADDRESS_BASE.format(ip, port))
      client.get(hash_str)
      client.close()
      return hash_str
    except:
      return None

  def __decrypt_memo(self, pri_key_str, txid):
    priv = account.PrivateKey(pri_key_str)
    tx = s.get_transaction(txid)
    from_acc = Account(tx['operations'][0][1]['from'], s)
    from_key = account.PublicKey(from_acc['owner']['key_auths'][0][0])
    to_acc = Account(tx['operations'][0][1]['to'], s)
    to_key = account.PublicKey(to_acc['owner']['key_auths'][0][0])
    message = tx['operations'][0][1]['memo']
    memo_str = memo.decode_memo(priv, message, from_key, to_key)
    json_obj = json.loads(memo_str[1:])
    key = json_obj['key']
    hash_str = json_obj['hash']
    ip = json_obj['ip']
    port = json_obj['port']
    return key, hash_str, ip, port

  def __init__(self, pri_key_str, txid):
    key, hash_str, ip, port = self.__decrypt_memo(pri_key_str, txid)
    if self.__download_file(hash_str, ip, port):
      self.__decrypt_file(key, hash_str)
      self.__filename = hash_str + '.dec'
    else:
      self.__filename = None

  def get_filename(self):
    return self.__filename

