#!/usr/bin/python3

import base64

# Cryptography Library
from cryptography.fernet import Fernet

# ECIES Library
import coincurve
from ecies import encrypt, decrypt

# Flask-RESTful Library
from flask import Flask
from flask_restful import Api, Resource, reqparse
import werkzeug

# BEOWULF Library
from beowulf.beowulfd import Beowulfd
from beowulfbase.account import PrivateKey

# IPFS HTTP Client Library
import ipfshttpclient

app = Flask(__name__)
api = Api(app)

# beowulfd_instance
s = Beowulfd()

class Ping(Resource):
  def get(self):
    return {'return_code': 0, 'message': 'OK'}

class UploadFile(Resource):
  def encrypt_key(self, pub_key, key_str):
    try:
      pub_point = pub_key.point()
      pub = coincurve.PublicKey.from_point(x=pub_point.x(), y=pub_point.y())
      return base64.urlsafe_b64encode(encrypt(pub.format(), key_str))
    except:
      return ''
  def decrypt_key(self, pri_key, key_enc_str):
    try:
      pri = coincurve.PrivateKey.from_hex(repr(pri_key))
      return decrypt(pri.to_hex(), base64.urlsafe_b64decode(key_enc_str))
    except:
      return ''
  def post(self):
    # Parse arguments
    parser = reqparse.RequestParser()
    parser.add_argument('file_data', type=werkzeug.datastructures.FileStorage, location='files')
    parser.add_argument('private_key')
    try:
      args = parser.parse_args()
    except:
      return {'return_code': 1, 'message': 'ERROR - Cannot parse arguments'}
    if not args['file_data'] or not args['private_key']:
      return {'return_code': 1, 'message': 'ERROR - Missing arguments'}
    # Get private and public keys
    try:
      pri_key = PrivateKey(args['private_key'])
      pub_key = pri_key.pubkey
    except:
      return {'return_code': 1, 'message': 'ERROR - Invalid private key format'}
    # Get info of file
    file_name = args['file_data'].filename
    file_data = args['file_data'].read()
    # Encrypt file
    key = Fernet.generate_key()
    f = Fernet(key)
    file_enc = base64.urlsafe_b64decode(f.encrypt(file_data))
    # Encrypt key
    key_enc = self.encrypt_key(pub_key, key)
    # Upload file
    # Broadcast TX
    # Return TXID

api.add_resource(Ping, '/ping')
api.add_resource(UploadFile, '/upload_file')

if __name__ == '__main__':
  app.run()
