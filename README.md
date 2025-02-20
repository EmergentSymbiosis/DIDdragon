# DIDdragon
# DID Validator

This script validates a Decentralized Identifier (DID) and verifies an ECDSA signature against the public key contained in a DID document. It supports DIDs in the `did:ethr`, `did:sol`, and `did:w3c` formats.

## Features
- **DID Validation**: Checks if the DID follows one of the supported formats.
- **Signature Verification**: Verifies an ECDSA signature against a public key embedded in the DID document.
- **Command-line Interface**: Provides a simple interface to input DIDs, did documents, and signatures for validation.

## Prerequisites
- Python 3.x installed on your system.
- The `ecdsa` library, which can be installed via pip:
  ```sh
  pip install ecdsa

