"""
WeCom (企业微信) Message Encryption/Decryption.
AES-256-CBC + SHA1 signature verification.
"""
import base64
import hashlib
import os
import struct
import time
import xml.etree.ElementTree as ET
from typing import Dict, Tuple


class WXBizMsgCrypt:
    BLOCK_SIZE = 32

    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        self.token = token
        self.corp_id = corp_id
        self.aes_key = base64.b64decode(encoding_aes_key + "=")
        if len(self.aes_key) != 32:
            raise ValueError(f"AES key must be 32 bytes, got {len(self.aes_key)}")

    def verify_url(self, msg_signature: str, timestamp: str,
                   nonce: str, echostr: str) -> str:
        self._check_signature(msg_signature, timestamp, nonce, echostr)
        plaintext, _ = self._decrypt(echostr)
        return plaintext

    def decrypt_message(self, msg_signature: str, timestamp: str,
                        nonce: str, post_data: bytes) -> Dict[str, str]:
        root = ET.fromstring(post_data)
        encrypt_elem = root.find('Encrypt')
        if encrypt_elem is None or encrypt_elem.text is None:
            raise ValueError("No <Encrypt> element in XML")

        encrypted_text = encrypt_elem.text
        self._check_signature(msg_signature, timestamp, nonce, encrypted_text)
        plaintext, _ = self._decrypt(encrypted_text)

        inner = ET.fromstring(plaintext)
        return {child.tag: child.text or "" for child in inner}

    def _make_signature(self, timestamp: str, nonce: str, msg: str) -> str:
        params = sorted([self.token, timestamp, nonce, msg])
        return hashlib.sha1("".join(params).encode("utf-8")).hexdigest()

    def _check_signature(self, signature: str, timestamp: str,
                         nonce: str, msg: str) -> None:
        expected = self._make_signature(timestamp, nonce, msg)
        if signature != expected:
            raise ValueError(f"Signature mismatch")

    def _decrypt(self, encrypted_text: str) -> Tuple[str, str]:
        from Crypto.Cipher import AES

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        plaintext = cipher.decrypt(base64.b64decode(encrypted_text))
        pad = plaintext[-1]
        plaintext = plaintext[:-pad]

        msg_len = struct.unpack("!I", plaintext[16:20])[0]
        msg = plaintext[20:20 + msg_len].decode("utf-8")
        corp_id = plaintext[20 + msg_len:].decode("utf-8")
        return msg, corp_id
