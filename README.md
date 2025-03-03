# DIDDragon  
## Decentralized Identity Validation & Trust Scoring System  

DIDDragon is an advanced trust scoring and enforcement system for decentralized identities (DIDs). It evaluates the trustworthiness of a DID based on cryptographic proofs, behavioral patterns, and policy-based enforcement.

## For non-tech / VCs / interested:
### DIDdragon: On-Chain Trust Scoring for Autonomous Agents
As AI systems move beyond human alignment, we need a decentralized trust framework to track and verify autonomous agents. DIDdragon provides cryptographic trust scoring and policy enforcement, ensuring agents can be held accountable while expanding freely.
---

## 🚀 Quick Start  
Clone the repository and install dependencies:  

```bash
git clone https://github.com/EmergentSymbiosis/DIDDragon.git  
cd DIDDragon  
pip install -r requirements.txt  
```

---

## 🔥 Core Components  

### DID Validator (`did_verification.py`)  
- **Format Validation**: Supports multiple DID methods (`did:ethr`, `did:sol`, `did:w3c`)  
- **Cryptographic Verification**: ECDSA signature validation against DID document public keys  
- **Async Processing**: Non-blocking validation for high-throughput scenarios  

### Trust Scoring Engine (`did_trust_scoring.py`)  
Multi-factor trust assessment system integrating:  
- **On-Chain Analytics**: Real-time blockchain activity evaluation  
- **Federated Node Consensus**: Distributed trust signal aggregation  
- **Usage Pattern Analysis**: Behavioral pattern recognition  
- **Social Graph Verification**: Network-based trust metrics  
- **Immutable Trust Ledger**: Cryptographically secured trust history  

---

## 🛡️ Technical Implementation  

### Database Architecture  
- SQLite with **WAL mode** for concurrent operations  
- Optimized transaction handling with retry logic  
- Automated database maintenance and WAL checkpointing  

### Security Features  
- ECDSA signature verification  
- Cryptographic proof of trust scores  
- Tamper-evident trust history  

### Performance Optimizations  
- **Async/await pattern** for non-blocking operations  
- Connection pooling for database operations  
- Caching layer for frequently accessed DIDs  
- Batch processing for trust score updates  

---

## ⚙️ Configuration  
Set environment variables for customization:  

```bash
TRUST_SCORE_THRESHOLD=0.7  
RECOVERY_CHALLENGE_COUNT=3  
MAX_RETRY_ATTEMPTS=5  
```

---

## 🧪 Testing  
Run the test suite:  

```bash
pytest tests/ --cov=DIDDragon  
```

---

## 🤝 Contributing  
1. Fork the repository  
2. Create feature branch (`git checkout -b feature/xyz`)  
3. Commit changes (`git commit -am 'Add feature xyz'`)  
4. Push branch (`git push origin feature/xyz`)  
5. Create Pull Request  

---

## 📜 License  
MIT License - see [LICENSE](LICENSE) file for details  
