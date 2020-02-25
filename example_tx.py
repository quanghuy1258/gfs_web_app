#!/usr/bin/python3

pri_key_str = "5JT8qLByKgeeqSCtnZWmMdBrzAcgfzCByRLZsuZUMdX4jowgvt1"
pub_key_str = "BEO6VeZsDrDbZKPKCRoHaKaoLVGuWhVX9F88uuaqnXwdBpCpngbXF"
memo_str = "Hello World"

# BEOWULF Library
from beowulf.beowulfd import Beowulfd
from beowulf.commit import Commit
from beowulf.account import Account
from beowulfbase import account

# beowulfd_instance
s = Beowulfd()

# Make TX
c = Commit(beowulfd_instance=s, keys = [pri_key_str])
from_acc = c.wallet.getAccountFromPrivateKey(pri_key_str)
to_acc = c.wallet.getAccountFromPublicKey(pub_key_str)
txid = c.transfer(account=from_acc, to=to_acc, amount='0.01', asset='W', fee='0.01', asset_fee='W', memo=memo_str)['id']

# Debug Infomation
print("TX ID = {}".format(txid))
tx = s.get_transaction(txid)
from_acc = Account(tx['operations'][0][1]['from'], s)
from_key = account.PublicKey(from_acc['owner']['key_auths'][0][0])
to_acc = Account(tx['operations'][0][1]['to'], s)
to_key = account.PublicKey(to_acc['owner']['key_auths'][0][0])
print("from_acc = {}".format(from_acc))
print("from_key = {}".format(from_key))
print("to_acc = {}".format(to_acc))
print("to_key = {}".format(to_key))
print("memo = {}".format(tx['operations'][0][1]['memo']))

