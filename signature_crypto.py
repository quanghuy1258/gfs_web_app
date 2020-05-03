import ecdsa
from beowulfbase.account import PublicKey, PrivateKey

def Sign(private_key_str, data):
  try:
    sign_key = ecdsa.SigningKey.from_secret_exponent(secexp=int(repr(PrivateKey(private_key_str)), 16), curve=ecdsa.SECP256k1)
    return sign_key.sign(data)
  except:
    return b""

def Verify(public_key_str, data, sign):
  try:
    verify_key = ecdsa.VerifyingKey.from_public_point(point=PublicKey(public_key_str).point(), curve=ecdsa.SECP256k1)
    return verify_key.verify(sign, data)
  except:
    return False
