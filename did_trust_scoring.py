import os
import sqlite3
import psycopg2
from datetime import datetime
import asyncio
import logging
import json
import hashlib
import time

# Set up logging
logging.basicConfig(filename='trust_scoring.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def init_wal_mode():
    """Enable SQLite WAL mode to prevent database locking."""
    try:
        with sqlite3.connect('did_trust_scores.db') as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.commit()
            logging.info("WAL mode initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing WAL mode: {e}")
        raise

# Database configuration
DATABASE_CONFIG = {
    'default': os.getenv('DB_BACKEND', 'sqlite'),  # Default to SQLite unless specified
    'backends': {
        'sqlite': {
            'ENGINE': 'sqlite3',
            'NAME': os.getenv('SQLITE_DB_NAME', 'did_trust_scores.db')
        },
        'postgresql': {
            'ENGINE': 'postgresql',
            'NAME': os.getenv('POSTGRESQL_DB_NAME', 'trust_db'),
            'USER': os.getenv('POSTGRESQL_DB_USER', 'user'),
            'PASSWORD': os.getenv('POSTGRESQL_DB_PASSWORD', 'password'),
            'HOST': os.getenv('POSTGRESQL_DB_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRESQL_DB_PORT', '5432')
        }
    }
}

# Get database connection
def get_database_connection():
    """Get a new database connection."""
    if DATABASE_CONFIG['default'] == 'sqlite':
        return sqlite3.connect('did_trust_scores.db', timeout=30, isolation_level=None)
    elif DATABASE_CONFIG['default'] == 'postgresql':
        return psycopg2.connect(
            dbname=DATABASE_CONFIG['backends']['postgresql']['NAME'],
            user=DATABASE_CONFIG['backends']['postgresql']['USER'],
            password=DATABASE_CONFIG['backends']['postgresql']['PASSWORD'],
            host=DATABASE_CONFIG['backends']['postgresql']['HOST'],
            port=DATABASE_CONFIG['backends']['postgresql']['PORT']
        )
    else:
        raise ValueError("Unsupported database backend")

# Initialize database connection
conn = get_database_connection()
c = conn.cursor()

# Initialize database and create tables
def init_db():
    """Initialize all database tables."""
    try:
        with get_database_connection() as conn:
            c = conn.cursor()
            
            # Create did_scores table
            c.execute('''
                CREATE TABLE IF NOT EXISTS did_scores (
                    did TEXT PRIMARY KEY, 
                    score REAL,
                    flagged INTEGER DEFAULT 0
                )
            ''')

            # Create policy_rules table
            c.execute('''
                CREATE TABLE IF NOT EXISTS policy_rules (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT UNIQUE,
                    min_trust_score REAL,
                    action TEXT
                )
            ''')

            # Create trust_ledger table
            c.execute('''
                CREATE TABLE IF NOT EXISTS trust_ledger (
                    did TEXT PRIMARY KEY,
                    trust_history TEXT
                )
            ''')

            conn.commit()
            logging.info("Database tables initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def hash_trust_score(did, score, timestamp):
    """Create a hash of the trust score data for verification."""
    data = f"{did}:{score}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def insert_trust_score(did, score):
    """Insert or update a DID trust score with cryptographic proof."""
    try:
        with get_database_connection() as conn:
            c = conn.cursor()
            timestamp = datetime.utcnow().isoformat()
            score_hash = hash_trust_score(did, score, timestamp)

            c.execute('''
                INSERT INTO did_scores (did, score, flagged) 
                VALUES (?, ?, 0)
                ON CONFLICT(did) DO UPDATE SET score = ?;
            ''', (did, score, score))

            c.execute('''
                INSERT INTO trust_ledger (did, trust_history)
                VALUES (?, ?)
                ON CONFLICT(did) DO UPDATE SET trust_history = ?;
            ''', (did, json.dumps([{"timestamp": timestamp, "trust_score": score, "hash": score_hash}]), 
                  json.dumps([{"timestamp": timestamp, "trust_score": score, "hash": score_hash}])))

            conn.commit()
            logging.debug(f'Inserted/Updated trust score for {did}: {score} | Hash: {score_hash}')
    except Exception as e:
        logging.error(f"Error inserting trust score for {did}: {e}")
        raise

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
    # Make sure database is initialized first
    init_db()
    
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
    try:
        # Initialize WAL mode before any other database operations
        init_wal_mode()
        
        # Initialize database tables
        init_db()
        
        # Create event loop
        loop = asyncio.get_event_loop()
        
        # Test DID
        test_did = 'did:ethr:123456789abcdef'
        
        # Run the trust score calculation
        final_score = loop.run_until_complete(aggregate_trust_score(test_did))
        
        # Print results
        print(f"Final Trust Score for {test_did}: {final_score}")
        
        # Clean up
        loop.close()
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

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
    try:
        with get_database_connection() as conn:
            c = conn.cursor()
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
    except Exception as e:
        logging.error(f"Error enforcing trust policy for {did}: {e}")
        raise

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

import sqlite3
import logging
import asyncio
import json
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    filename='trust_recovery.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize SQLite database
conn = sqlite3.connect('did_trust_scores.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS trust_recovery (
                did TEXT PRIMARY KEY, 
                recovery_stage TEXT,
                last_attempt TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS trust_ledger (
                did TEXT PRIMARY KEY,
                trust_history TEXT
            )''')

conn.commit()

### 🔥 Trust Repair Mechanism for Flagged DIDs
def initiate_trust_recovery(did):
    """Start a recovery process for a flagged DID."""
    c.execute('SELECT flagged FROM did_scores WHERE did = ?', (did,))
    result = c.fetchone()
    
    if not result or result[0] == 0:
        logging.info(f"DID {did} is not flagged. No recovery needed.")
        return "DID is not flagged."

    c.execute('''INSERT INTO trust_recovery (did, recovery_stage, last_attempt, status)
                 VALUES (?, ?, ?, 'pending') 
                 ON CONFLICT(did) DO UPDATE SET last_attempt = ?''',
              (did, 'start', datetime.now(), datetime.now()))
    
    conn.commit()
    logging.info(f"Trust recovery process initiated for DID {did}.")
    return f"Trust recovery started for {did}. Awaiting verification steps."

### 🔥 Verification Challenge System for Reputation Recovery
def verify_trust_recovery(did, verification_proof):
    """Verify a DID's recovery attempt based on submitted proof."""
    c.execute('SELECT status FROM trust_recovery WHERE did = ?', (did,))
    result = c.fetchone()

    if not result or result[0] != 'pending':
        logging.info(f"DID {did} has no active recovery process.")
        return "No active recovery process."

    # 🔹 Placeholder: Implement actual proof validation with federated identity verification
    verified = validate_verification_proof(verification_proof)

    if verified:
        c.execute('UPDATE trust_recovery SET status = "verified" WHERE did = ?', (did,))
        unflag_did(did)
        logging.info(f"DID {did} has successfully recovered trust.")
        return f"DID {did} has recovered trust successfully."
    else:
        c.execute('UPDATE trust_recovery SET status = "rejected" WHERE did = ?', (did,))
        logging.warning(f"Trust recovery for {did} failed.")
        return f"DID {did} failed recovery verification."

def validate_verification_proof(proof):
    """Placeholder function to validate verification proof."""
    # TODO: Implement actual verification logic (e.g., checking blockchain signatures, federated confirmations)
    return proof == "valid_proof"

### 🔥 Historical Trust Ledger for Trust Repair Speed
def update_trust_ledger(did, trust_score):
    """Update trust ledger with retry logic to prevent database lock errors."""
    retries = 5  # Number of retries before failing
    delay = 0.5  # Initial delay for retrying

    for attempt in range(retries):
        try:
            with sqlite3.connect('did_trust_scores.db', timeout=10, check_same_thread=False) as conn:
                conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')  # Clear WAL
                conn.execute('PRAGMA journal_mode=WAL')  # Ensure WAL mode
                conn.execute('PRAGMA busy_timeout = 5000;')  # Increase timeout
                
                c = conn.cursor()
                c.execute("PRAGMA quick_check;")  # Check if DB is corrupted
                
                # Ensure transaction safety
                conn.execute('BEGIN IMMEDIATE;')  
                
                # Get existing trust history
                c.execute('SELECT trust_history FROM trust_ledger WHERE did = ?', (did,))
                result = c.fetchone()

                # Update trust history
                trust_history = json.loads(result[0]) if result else []
                trust_history.append({
                    "timestamp": str(datetime.now()),
                    "trust_score": trust_score
                })

                # Insert or update with new history
                c.execute('''
                    INSERT INTO trust_ledger (did, trust_history) 
                    VALUES (?, ?)
                    ON CONFLICT(did) DO UPDATE SET trust_history = ?
                ''', (
                    did, 
                    json.dumps(trust_history), 
                    json.dumps(trust_history)
                ))
                
                conn.commit()  # Commit transaction
                return  # Exit if successful
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logging.warning(f"⚠️ Database is locked. Retrying {attempt+1}/{retries}...")
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            else:
                logging.error(f"Database error: {e}")
                raise
        except Exception as e:
            logging.error(f"Error updating trust ledger for {did}: {e}")
            raise

from datetime import timedelta

def apply_decay_model(did):
    """Apply dynamic trust decay based on behavior & inactivity."""
    c.execute('SELECT trust_history FROM trust_ledger WHERE did = ?', (did,))
    result = c.fetchone()

    if not result:
        return 1  # Default recovery speed for new DIDs

    trust_history = json.loads(result[0])
    oldest_entry = min(trust_history, key=lambda x: datetime.fromisoformat(x['timestamp']))
    time_since_first_flag = datetime.utcnow() - datetime.fromisoformat(oldest_entry['timestamp'])

    # Decay is more aggressive if flagged multiple times
    c.execute('SELECT flagged FROM did_scores WHERE did = ?', (did,))
    flagged_result = c.fetchone()
    is_flagged = flagged_result[0] if flagged_result else 0

    # Decay model: faster decay for flagged users, slower for active ones
    if is_flagged:
        return 0.3 if time_since_first_flag > timedelta(days=180) else 0.6  # Stronger penalty for flagged users
    else:
        return 0.8 if time_since_first_flag > timedelta(days=180) else 1  # Slower decay for normal users

### 🔥 Automated Gradual Trust Score Adjustments Based on Recovery Progress
async def periodic_trust_repair():
    """Periodically attempt to repair flagged DIDs' trust scores based on recovery progress."""
    while True:
        c.execute('SELECT did FROM trust_recovery WHERE status = "pending"')
        dids = c.fetchall()

        for (did,) in dids:
            recovery_multiplier = apply_decay_model(did)
            current_score = get_current_trust_score(did)
            new_score = min(current_score + (0.1 * recovery_multiplier), 1.0)
            update_trust_score(did, new_score)
            logging.info(f"Gradual trust recovery applied to {did}, new score: {new_score}")

        await asyncio.sleep(24 * 60 * 60)  # Run every 24 hours

# Helper functions (replace with actual database logic)
def get_current_trust_score(did):
    """Get the current trust score for a DID."""
    try:
        with get_database_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT score FROM did_scores WHERE did = ?', (did,))
            result = c.fetchone()
            return result[0] if result else 0.0
    except Exception as e:
        logging.error(f"Error getting trust score for {did}: {e}")
        return 0.0

def update_trust_score(did, new_score):
    c.execute('UPDATE did_scores SET score = ? WHERE did = ?', (new_score, did))
    conn.commit()

def unflag_did(did):
    """Remove a flag from a DID if trust score improves."""
    c.execute('UPDATE did_scores SET flagged = 0 WHERE did = ?', (did,))
    conn.commit()
    logging.info(f"DID {did} has been restored to normal status.")

# Example Usage
if __name__ == "__main__":
    test_did = 'did:ethr:123456789abcdef'
    print(initiate_trust_recovery(test_did))
    print(verify_trust_recovery(test_did, "valid_proof"))
    update_trust_ledger(test_did, get_current_trust_score(test_did))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(periodic_trust_repair())

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect('trust_scores.db')
    c = conn.cursor()
    
    # Create trust_ledger table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS trust_ledger (
            did TEXT PRIMARY KEY,
            trust_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_trust_score(did, trust_score):
    """Insert or update trust score for a DID."""
    conn = sqlite3.connect('trust_scores.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO trust_ledger (did, trust_score)
        VALUES (?, ?)
    ''', (did, trust_score))
    
    conn.commit()
    conn.close()

# Call init_db at the start of the program
if __name__ == "__main__":
    init_db()  # Initialize database before running main logic
    # ... rest of your main code ...




