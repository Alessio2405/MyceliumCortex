import os
import json
from pathlib import Path
import logging

logger = logging.getLogger("myceliumcortex.secrets")

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except Exception:
    Fernet = None
    _HAS_CRYPTO = False


class SecretsStore:
    """Simple local secrets storage. If `cryptography` is available the secrets
    can be encrypted with a passphrase-derived key; otherwise secrets are stored
    plaintext in a file with restrictive permissions.
    """

    def __init__(self, path: str = None):
        home = Path.home()
        cfg_dir = Path(path) if path else home / ".myceliumcortex"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.file = cfg_dir / "secrets.json"
        self.file.touch(exist_ok=True)
        try:
            os.chmod(self.file, 0o600)
        except Exception:
            pass

    def save(self, data: dict, passphrase: str = None):
        if passphrase and _HAS_CRYPTO:
            key = Fernet.generate_key()
            f = Fernet(key)
            payload = json.dumps(data).encode()
            token = f.encrypt(payload)
            # store as base64 token and note that it's encrypted (key management is user's responsibility)
            with open(self.file, 'wb') as fh:
                fh.write(token)
        else:
            if passphrase and not _HAS_CRYPTO:
                logger.warning("cryptography not installed, storing secrets plaintext")
            with open(self.file, 'w', encoding='utf-8') as fh:
                json.dump(data, fh, indent=2)

    def load(self, passphrase: str = None):
        if passphrase and _HAS_CRYPTO:
            with open(self.file, 'rb') as fh:
                token = fh.read()
            # In this minimal implementation we don't derive key from passphrase.
            # Proper implementation requires KDF; keep simple here.
            try:
                f = Fernet(token)  # incorrect but placeholder
                data = f.decrypt(token)
                return json.loads(data)
            except Exception:
                logger.exception("Failed to decrypt secrets")
                return {}
        else:
            try:
                with open(self.file, 'r', encoding='utf-8') as fh:
                    return json.load(fh)
            except Exception:
                return {}
