
import firebase_admin
from firebase_admin import credentials
import os

if not firebase_admin._apps:
    cred_path = os.path.join('config', 'firebase-service-account.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
