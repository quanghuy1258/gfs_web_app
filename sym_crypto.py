import os, hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def SymEncrypt(key, plaintext):
  try:
    block_bits = algorithms.AES.block_size
    block_bytes = algorithms.AES.block_size // 8

    key = hashlib.sha512(key).digest()[:32] # Use SHA-512 algorithm but keep only first 32 bytes
    iv = os.urandom(block_bytes)

    padder = padding.PKCS7(block_bits).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).encryptor()

    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    iv_ciphertext = iv + ciphertext
    return iv_ciphertext
  except:
    return b""

def SymDecrypt(key, iv_ciphertext):
  try:
    block_bits = algorithms.AES.block_size
    block_bytes = algorithms.AES.block_size // 8

    key = hashlib.sha512(key).digest()[:32] # Use SHA-512 algorithm but keep only first 32 bytes
    iv, ciphertext = iv_ciphertext[:block_bytes], iv_ciphertext[block_bytes:]

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()

    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(block_bits).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext
  except:
    return b""
