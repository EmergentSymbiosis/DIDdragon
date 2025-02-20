import re
import argparse

class DIDVerifier:
    def __init__(self):
        self.did_patterns = {
            'ethr': r'^did:ethr:[0-9a-fA-F]{40}$',
            'sol': r'^did:sol:[1-9A-HJ-NP-Za-km-z]{32,44}$',
            'w3c': r'^did:w3c:[1-9a-zA-Z_-]+$'
        }

    def validate(self, did):
        """Validate the DID format and return the matching type."""
        for key, pattern in self.did_patterns.items():
            if re.match(pattern, did):
                return key
        raise ValueError("Unsupported DID format")

    def is_valid(self, did):
        """Check if the DID follows a recognized format."""
        try:
            self.validate(did)
            return True
        except ValueError:
            return False

def main():
    parser = argparse.ArgumentParser(description="DID Validator")
    parser.add_argument('did', type=str, help="Decentralized Identifier to validate")
    args = parser.parse_args()
    did = args.did

    verifier = DIDVerifier()

    if verifier.is_valid(did):
        did_type = verifier.validate(did)
        print(f"The DID {did} is valid and uses the '{did_type}' format.")
    else:
        print(f"The DID {did} is invalid.")

if __name__ == "__main__":
    main()
