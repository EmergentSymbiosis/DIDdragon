import sqlite3
from datetime import datetime
import asyncio
import logging

# Set up logging
logging.basicConfig(filename='trust_scoring.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SQLite database
conn = sqlite3.connect('did_trust_scores.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS did_scores (
        did TEXT PRIMARY KEY, 
        score REAL
    )
''')
conn.commit()

# Function to insert trust scores securely (prevents duplicates)
def insert_trust_score(did, score):
    """Insert or update a DID trust score."""
    c.execute('INSERT INTO did_scores (did, score) VALUES (?, ?) ON CONFLICT(did) DO UPDATE SET score=?', 
              (did, score, score))
    conn.commit()
    logging.debug(f'Inserted/Updated trust score for {did}: {score}')

# Function to retrieve trust scores securely
def get_trust_score(did):
    """Retrieve the trust score of a DID."""
    c.execute('SELECT score FROM did_scores WHERE did = ?', (did,))
    result = c.fetchone()
    return result[0] if result else None

# Placeholder functions for fetching verification data, to be implemented based on actual API/endpoints
async def fetch_onchain_proofs(did):
    """Fetch trust score from blockchain records."""
    try:
        # TODO: Implement actual blockchain API call
        return {'score': 0.8}
    except Exception as e:
        logging.error(f"Error fetching on-chain data for {did}: {e}")
        return {'score': 0.0}

async def fetch_federated_nodes(did):
    """Fetch trust score from federated nodes."""
    try:
        # TODO: Implement federated node query
        return {'score': 0.7}
    except Exception as e:
        logging.error(f"Error fetching federated data for {did}: {e}")
        return {'score': 0.0}

async def fetch_usage_patterns(did):
    """Fetch historical usage data for DID."""
    try:
        # TODO: Implement logic to fetch usage data
        return {'score': 0.6}
    except Exception as e:
        logging.error(f"Error fetching usage pattern data for {did}: {e}")
        return {'score': 0.0}

async def fetch_social_signals(did):
    """Fetch social verification signals for DID."""
    try:
        # TODO: Implement API call to social verification sources
        return {'score': 0.5}
    except Exception as e:
        logging.error(f"Error fetching social verification data for {did}: {e}")
        return {'score': 0.0}

# Function to aggregate trust scores from all sources
async def aggregate_trust_score(did):
    """Aggregate and compute a trust score for a DID."""
    onchain_data = await fetch_onchain_proofs(did)
    federated_data = await fetch_federated_nodes(did)
    usage_data = await fetch_usage_patterns(did)
    social_data = await fetch_social_signals(did)

    # Normalize all scores to 0-1 range
    onchain_score = min(onchain_data['score'], 1.0)
    federated_score = min(federated_data['score'], 1.0)
    usage_score = min(usage_data['score'], 1.0)
    social_score = min(social_data['score'], 1.0)

    # Define weights for each source (sum should be 1)
    weights = {
        'onchain': 0.3,
        'federated': 0.2,
        'usage': 0.15,
        'social': 0.35
    }

    # Calculate weighted trust score
    trust_score = (weights['onchain'] * onchain_score +
                   weights['federated'] * federated_score +
                   weights['usage'] * usage_score +
                   weights['social'] * social_score)

    insert_trust_score(did, trust_score)
    return trust_score

# Periodic Task for Data Aggregation, disabled during manual testing
# async def update_trust_scores():
#     while True:
#         # TODO: Fetch all active DIDs from database
#         did_list = ["did:ethr:123456789abcdef"]  # Placeholder for now
#         for did in did_list:
#             await aggregate_trust_score(did)
#             logging.info(f"Updated trust score for {did}")
#         await asyncio.sleep(7 * 24 * 60 * 60)  # Runs every 7 days

# Example Usage, disabled during manual testing
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    test_did = 'did:ethr:123456789abcdef'
    final_score = loop.run_until_complete(aggregate_trust_score(test_did))
    print(f"Final Trust Score for {test_did}: {final_score}")

    # Start periodic updates (disabled for manual testing)
    # loop.run_until_complete(update_trust_scores())

import sqlite3
import logging
import asyncio
from datetime import datetime

# Set up logging
logging.basicConfig(filename='trust_enforcement.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SQLite database
conn = sqlite3.connect('did_trust_scores.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS did_scores (
        did TEXT PRIMARY KEY, 
        score REAL,
        flagged INTEGER DEFAULT 0  -- 1 = flagged, 0 = normal
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS policy_rules (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT UNIQUE,
        min_trust_score REAL,
        action TEXT  -- Actions: "alert", "restrict", "review"
    )
''')

conn.commit()

### 🔥 Policy Engine: Enforce Trust-Based Actions
def enforce_trust_policy(did):
    """Evaluate a DID against trust policies and determine actions."""
    c.execute('SELECT score FROM did_scores WHERE did = ?', (did,))
    result = c.fetchone()
    
    if not result:
        logging.warning(f"DID {did} not found in trust scores.")
        return "DID not found"

    trust_score = result[0]

    # Fetch active rules
    c.execute('SELECT rule_name, min_trust_score, action FROM policy_rules')
    rules = c.fetchall()

    for rule_name, min_score, action in rules:
        if trust_score < min_score:
            logging.warning(f"DID {did} flagged under rule '{rule_name}' - Action: {action}")

            if action == "alert":
                return f"DID {did} triggered an alert under rule '{rule_name}'."
            elif action == "restrict":
                flag_did(did)
                return f"DID {did} has been restricted under rule '{rule_name}'."
            elif action == "review":
                return f"DID {did} requires manual review under rule '{rule_name}'."

    return f"DID {did} passes all trust policies."

### 🔥 Flagging System for Risky DIDs
def flag_did(did):
    """Flag a DID as untrusted."""
    c.execute('UPDATE did_scores SET flagged = 1 WHERE did = ?', (did,))
    conn.commit()
    logging.warning(f"DID {did} has been flagged as untrusted.")

def unflag_did(did):
    """Remove a flag from a DID if trust score improves."""
    c.execute('UPDATE did_scores SET flagged = 0 WHERE did = ?', (did,))
    conn.commit()
    logging.info(f"DID {did} has been restored to normal status.")

### 🔥 Rule Management for Decentralized Trust Enforcement
def add_policy_rule(rule_name, min_trust_score, action):
    """Add a trust enforcement rule."""
    try:
        c.execute('''
            INSERT INTO policy_rules (rule_name, min_trust_score, action) 
            VALUES (?, ?, ?)''', (rule_name, min_trust_score, action))
        conn.commit()
        logging.info(f"Added new policy rule: {rule_name} (Min Trust: {min_trust_score}, Action: {action})")
    except sqlite3.IntegrityError:
        logging.warning(f"Policy rule '{rule_name}' already exists.")

def remove_policy_rule(rule_name):
    """Remove a trust enforcement rule."""
    c.execute('DELETE FROM policy_rules WHERE rule_name = ?', (rule_name,))
    conn.commit()
    logging.info(f"Removed policy rule: {rule_name}")

### 🔥 Example: Automate Trust Enforcement
async def auto_enforce_trust():
    """Run automated trust enforcement checks periodically."""
    while True:
        c.execute('SELECT did FROM did_scores')
        dids = c.fetchall()

        for (did,) in dids:
            result = enforce_trust_policy(did)
            logging.info(result)

        await asyncio.sleep(24 * 60 * 60)  # Run every 24 hours

### 🔥 Example Usage
if __name__ == "__main__":
    test_did = 'did:ethr:123456789abcdef'
    
    # Example: Add trust policy rules
    add_policy_rule("Low Trust Restriction", 0.4, "restrict")
    add_policy_rule("Moderate Trust Alert", 0.6, "alert")
    add_policy_rule("Review for High Risk", 0.3, "review")

    # Example: Enforce trust rules on a DID
    print(enforce_trust_policy(test_did))

