import coincurve
from ecies import encrypt, decrypt
from beowulfbase.account import PublicKey, PrivateKey

def AsymEncrypt(public_key_str, plaintext):
  try:
    public_point = PublicKey(public_key_str).point()
    public_key = coincurve.PublicKey.from_point(x=public_point.x(), y=public_point.y())
    return encrypt(public_key.format(True), plaintext)
  except:
    return b""

def AsymDecrypt(private_key_str, ciphertext):
  try:
    private_key = coincurve.PrivateKey.from_hex(repr(PrivateKey(private_key_str)))
    return decrypt(private_key.secret, ciphertext)
  except:
    return b""
