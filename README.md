# DIDDragon  
## DID Validator & Trust Scoring System  

This repository implements a **DID Validator** for **Decentralized Identifiers (DIDs)** and a **DID Trust Scoring Module** to assess and verify trustworthiness based on multiple sources.  

## Features  

### DID Validator (`did_verification.py`)  
- **DID Validation**: Checks if the DID follows one of the supported formats (`did:ethr`, `did:sol`, `did:w3c`).  
- **Signature Verification**: Verifies an **ECDSA signature** against the public key embedded in the DID document.  
- **Command-Line Interface**: Provides a simple way to input and validate DIDs.  

### DID Trust Scoring Module (`did_trust_scoring.py`)  
The **DID Trust Scoring Module** extends DID verification by assigning a **trust score** based on multiple verification sources, including:  

1. **On-Chain Proofs** - Evaluates blockchain activity.  
2. **Federated Verification Nodes** - Checks trust signals from decentralized identity systems.  
3. **Usage History** - Analyzes past DID activity.  
4. **Social Verification** - Assesses trustworthiness via external community signals.  

## Installation  

Ensure you have **Python 3.x** installed, along with necessary dependencies:  


## Running the DID Verification System  
To validate a DID:  
python did_verification.py


## Running the Trust Scoring System  
To verify and score a DID:  
python did_trust_scoring.py

To retrieve an existing trust score programmatically:  
from did_trust_scoring import get_trust_score
score = get_trust_score("did:ethr:123456789abcdef") print(f"Trust Score: {score}")


## How It Works  

- When a DID is verified, the system **fetches trust signals** from multiple sources.  
- It **aggregates scores using a weighted model**, ensuring that **more reliable sources contribute more to the final trust score**.  
- The **final trust score is stored securely in a SQLite database** and **updated dynamically as new data is fetched**.  

## Next Steps  

- **Automate trust score updates using periodic data fetching.**  
- **Optimize performance for large-scale decentralized identity networks.**  
- **Enhance logging and error handling for real-world deployment.**  








