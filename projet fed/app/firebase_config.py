import firebase_admin
from firebase_admin import credentials, firestore

# Charger la clé de configuration Firebase
cred = credentials.Certificate("firebase_config.json")  # Vérifie que le chemin est correct
firebase_admin.initialize_app(cred)

# Initialiser Firestore
db = firestore.client()
