import os
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)

# Initialize Firestore client globally
db = None

def initialize_firestore():
    """
    Initializes the Firestore client.
    Assumes GOOGLE_APPLICATION_CREDENTIALS environment variable is set
    or running in a Google Cloud environment.
    """
    global db
    if db is None:
        try:
            db = firestore.Client()
            logger.info("Firestore client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firestore client: {e}")
            db = None # Ensure db is None if initialization fails

def store_conversation(chat_id: int, user_query: str, bot_response: str):
    """
    Stores a user query and bot response in a Firestore collection.
    """
    if db is None:
        logger.warning("Firestore client not initialized. Cannot store conversation.")
        return

    try:
        collection_ref = db.collection('conversations')
        doc_ref = collection_ref.document() # Let Firestore generate a unique ID

        doc_ref.set({
            'chat_id': str(chat_id),
            'user_query': user_query,
            'bot_response': bot_response,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logger.info(f"Conversation stored for chat_id {chat_id}.")
    except Exception as e:
        logger.error(f"Error storing conversation for chat_id {chat_id}: {e}")

def store_report(chat_id: int, user_query: str, bot_response: str):
    """
    Stores a user prompt and bot response as a report in a Firestore collection.
    """
    if db is None:
        logger.warning("Firestore client not initialized. Cannot store report.")
        return

    try:
        collection_ref = db.collection('reports')
        doc_ref = collection_ref.document() # Let Firestore generate a unique ID

        doc_ref.set({
            'chat_id': str(chat_id),
            'reported_query': user_query,
            'reported_response': bot_response,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logger.info(f"Report stored for chat_id {chat_id}.")
    except Exception as e:
        logger.error(f"Error storing report for chat_id {chat_id}: {e}")

# Call initialize_firestore when this module is imported
initialize_firestore()
