#!/usr/bin/python3

import base64

# Flask-RESTful Library
from flask import Flask
from flask_restful import Api, Resource, reqparse
import werkzeug

# Cryptography Library
from cryptography.fernet import Fernet

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
    # Encrypt file
    key_b64 = Fernet.generate_key()
    key = base64.urlsafe_b64decode(key_b64)
    f = Fernet(key_b64)
    file_enc_b64 = f.encrypt(args['file_data'].read())
    file_enc = base64.urlsafe_b64decode(file_enc_b64)
    # Encrypt key
    # Upload file
    # Broadcast TX
    # Return TXID

api.add_resource(Ping, '/ping')
api.add_resource(UploadFile, '/upload_file')

if __name__ == '__main__':
  app.run()
