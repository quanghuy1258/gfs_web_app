#!/usr/bin/python3

import json, random, base64, math

# Cryptography Library
from cryptography.fernet import Fernet

# Crypto Library
from Crypto.Cipher import AES
from Crypto import Random

# BEOWULF Library
from beowulf.beowulfd import Beowulfd
from beowulf.commit import Commit
from beowulf.account import Account
from beowulfbase import account

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

class UploadFile():
  def __encrypt_file(self, file_path):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    with open(file_path, 'rb') as file_obj:
      with open(file_path + '.enc', 'wb') as file_enc_obj:
        file_enc_obj.write(base64.urlsafe_b64decode(fernet.encrypt(file_obj.read())))
    key_bin = base64.urlsafe_b64decode(key)
    return key_bin

  def __upload_file(self, ipfs_master, file_path):
    client = ipfs_master.getClient()
    hash_str = client.add(file_path)['Hash']
    client.close()
    hash_bin = hash_str[2:].encode('ascii')
    hash_bin = base64.urlsafe_b64decode(hash_bin)
    return hash_bin

  def __create_memo(self, key, hash_bin):
    memo_bin = key + hash_bin
    return memo_bin

  def __create_shared_key(self, priv, pub):
    pub_point = pub.point()
    priv_point = int(repr(priv), 16)
    shared_point = pub_point * priv_point
    x = shared_point.x()
    shared_key = x.to_bytes(max(math.ceil(x.bit_length()/8), 16), 'little')[:16]
    return shared_key

  def __encrypt_memo(self, priv, pub, memo_bin):
    key = self.__create_shared_key(priv, pub)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    memo_bin = iv + cipher.encrypt(memo_bin)
    memo_str = base64.urlsafe_b64encode(memo_bin).decode('ascii')
    return memo_str

  def __make_tx(self, pri_key_str, pub_key_str, memo_str):
    c = Commit(beowulfd_instance=s, keys = [pri_key_str])
    from_acc = c.wallet.getAccountFromPrivateKey(pri_key_str)
    to_acc = c.wallet.getAccountFromPublicKey(pub_key_str)
    txid = c.transfer(account=from_acc, to=to_acc, amount='0.01', asset='W', fee='0.01', asset_fee='W', memo=memo_str)['id']
    return txid

  def __init__(self, file_path, ipfs_master, pri_key_sender, pub_key_receiver):
    key_bin = self.__encrypt_file(file_path)
    hash_bin = self.__upload_file(ipfs_master, file_path + '.enc')
    memo_bin = self.__create_memo(key_bin, hash_bin)
    priv = account.PrivateKey(pri_key_sender)
    pub = account.PublicKey(pub_key_receiver)
    memo_str = self.__encrypt_memo(priv, pub, memo_bin)
    self.__txid = self.__make_tx(pri_key_sender, pub_key_receiver, memo_str)

  def get_txid(self):
    return self.__txid

class DownloadFile():
  def __decrypt_file(self, key_bin, file_enc_name):
    key = base64.urlsafe_b64encode(key_bin)
    fernet = Fernet(key)
    with open(file_enc_name, 'rb') as file_enc_obj:
      with open(file_enc_name + '.dec', 'wb') as file_obj:
        file_obj.write(fernet.decrypt(base64.urlsafe_b64encode(file_enc_obj.read())))

  def __download_file(self, ipfs_master, hash_bin):
    hash_bin = base64.urlsafe_b64encode(hash_bin)
    hash_str = 'Qm' + hash_bin.decode('ascii')
    client = ipfs_master.getClient()
    client.get(hash_str)
    client.close()
    return hash_str

  def __create_shared_key(self, priv, pub):
    pub_point = pub.point()
    priv_point = int(repr(priv), 16)
    shared_point = pub_point * priv_point
    x = shared_point.x()
    shared_key = x.to_bytes(max(math.ceil(x.bit_length()/8), 16), 'little')[:16]
    return shared_key

  def __decrypt_memo(self, pri_key_str, txid):
    priv = account.PrivateKey(pri_key_str)
    tx = s.get_transaction(txid)
    from_acc = Account(tx['operations'][0][1]['from'], s)
    from_key = account.PublicKey(from_acc['owner']['key_auths'][0][0])
    to_acc = Account(tx['operations'][0][1]['to'], s)
    to_key = account.PublicKey(to_acc['owner']['key_auths'][0][0])
    key = None
    if repr(from_key) == repr(priv.pubkey):
      key = self.__create_shared_key(priv, from_key)
    if repr(to_key) == repr(priv.pubkey):
      key = self.__create_shared_key(priv, to_key)
    ciphertext = tx['operations'][0][1]['memo']
    ciphertext_bin = ciphertext.encode('ascii')
    ciphertext_bin = base64.urlsafe_b64decode(ciphertext_bin)
    iv = ciphertext_bin[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    message_bin = cipher.decrypt(ciphertext_bin[AES.block_size:])
    key_bin = message_bin[:32]
    hash_bin = message_bin[32:]
    return key_bin, hash_bin

  def __init__(self, ipfs_master, pri_key_str, txid):
    key_bin, hash_bin = self.__decrypt_memo(pri_key_str, txid)
    hash_str = self.__download_file(ipfs_master, hash_bin)
    self.__decrypt_file(key_bin, hash_str)
    self.__filename = hash_str + '.dec'

  def get_filename(self):
    return self.__filename

