import re
import asyncio
import argparse

class DIDVerifier:
    def __init__(self):
        self.did_patterns = {
            'ethr': r'^did:ethr:(?:0x)?[0-9a-fA-F]{40}$',
            'sol': r'^did:sol:[1-9A-HJ-NP-Za-km-z]{32,44}$',
            'w3c': r'^did:w3c:[1-9a-zA-Z_-]+$',
            'agent': r'^did:agent:[a-zA-Z0-9_-]+$',  # New pattern for AI agents
            'fed': r'^did:fed:[a-zA-Z0-9_-]+$'  # New pattern for federated systems
        }

    def validate(self, did):
        """Validate the DID format and return the matching type."""
        for key, pattern in self.did_patterns.items():
            if re.match(pattern, did):
                return key
        raise ValueError("Unsupported DID format")

    async def fetch_metadata(self, did):
        """Fetch metadata for a DID to verify its legitimacy."""
        did_type = self.validate(did)
        
        if did_type in ["ethr", "sol"]:
            return await self.fetch_onchain_metadata(did)
        elif did_type in ["agent", "fed"]:
            return await self.fetch_offchain_metadata(did)
        else:
            return {"status": "unknown", "details": "No verification method available"}

    async def fetch_onchain_metadata(self, did):
        """Mock function to simulate on-chain verification."""
        await asyncio.sleep(1)  # Simulating async call
        return {"status": "verified", "source": "on-chain"}

    async def fetch_offchain_metadata(self, did):
        """Mock function to simulate off-chain verification."""
        await asyncio.sleep(1)  # Simulating async call
        return {"status": "verified", "source": "federated verification"}

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
