# DIDDragon  
## DID Validator & Trust Scoring System  

This repository implements a DID Validator for Decentralized Identifiers (DIDs) and a DID Trust Scoring Module to assess and verify trustworthiness based on multiple sources. It also includes **Decentralized Trust Enforcement (DTE)** for risk flagging, trust-based policies, and a recovery system for flagged identities.  

## Features  

### DID Validator (`did_verification.py`)  
- **DID Validation**: Checks if the DID follows one of the supported formats (`did:ethr`, `did:sol`, `did:w3c`).  
- **Signature Verification**: Verifies an **ECDSA signature** against the public key embedded in the DID document.  
- **Command-Line Interface**: Provides a simple way to input and validate DIDs.  

### DID Trust Scoring Module (`did_trust_scoring.py`)  
The **DID Trust Scoring Module** extends DID verification by assigning a **trust score** based on multiple verification sources, including:  
- **On-Chain Proofs** - Evaluates blockchain activity.  
- **Federated Verification Nodes** - Checks trust signals from decentralized identity systems.  
- **Usage History** - Analyzes past DID activity.  
- **Social Verification** - Assesses trustworthiness via external community signals.  
- **Trust Ledger** - Maintains a historical record of DID interactions for recovery and long-term trust assessment.  

### Decentralized Trust Enforcement (DTE) (`did_trust_enforcement.py`)  
The **DTE system** adds **trust-based access control** to DID verification by:  
- **Flagging Risky DIDs** - DIDs with low trust scores are **automatically flagged** for review.  
- **Policy Engine** - Enforces **trust-based rules** (e.g., restricting low-trust DIDs from executing actions).  
- **Dynamic Trust Score Adjustments** - Ensures that DID reputations **update in real time** based on behavior.  

### Identity Recovery & Self-Healing Trust (`did_trust_recovery.py`)  
- **Trust Repair Mechanism** - Allows flagged DIDs to **recover their trust score** based on predefined verification steps.  
- **Verification Challenge System** - Requires flagged DIDs to **prove their trustworthiness** through community validation.  
- **Historical Trust Ledger** - Influences **recovery speed** based on past behavior, ensuring fair but robust recovery.  
- **Automated Trust Score Adjustments** - Gradually increases scores for compliant DIDs **without manual intervention**.  

## Installation  
Ensure you have **Python 3.x** installed, along with necessary dependencies:  
```sh
pip install ecdsa sqlite3

## Usage  
### Running the DID Verification System  
```sh
python did_verification.py
Running the Trust Scoring System
python did_trust_scoring.py
Retrieving an Existing Trust Score
from did_trust_scoring import get_trust_score
score = get_trust_score("did:ethr:123456789abcdef") 
print(f"Trust Score: {score}")



