import re

class DIDVerifier:
    DID_PATTERN = r"^did:[a-z0-9]+:[a-zA-Z0-9.\-_]+$"

    def __init__(self, did):
        self.did = did

    def is_valid_did(self):
        """Check if the DID follows a proper structure."""
        return bool(re.match(self.DID_PATTERN, self.did))

# Example usage
if __name__ == "__main__":
    did = "did:example:123456789abcdef"
    verifier = DIDVerifier(did)
    print(f"Is DID valid? {verifier.is_valid_did()}")
