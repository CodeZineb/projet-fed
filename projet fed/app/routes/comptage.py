from flask import Blueprint, render_template, flash
from app.firebase_config import db
import base64
from app.email_utils import send_email

de_email = "nouhila.boudad@gmail.com"  # Adresse email de DE

# Créer un blueprint pour le centre de comptage
comptage_bp = Blueprint('comptage', __name__, url_prefix='/comptage')

@comptage_bp.route('/', methods=['GET'])
def comptage():
    try:
        # Récupérer tous les votes depuis Firestore
        votes_ref = db.collection('votes')
        votes_docs = votes_ref.stream()

        # Préparer les votes pour le template
        votes = []
        for doc in votes_docs:
            data = doc.to_dict()
            votes.append({
                'nom': data.get('nom'),
                'prenom': data.get('prenom'),
                'date_naissance': data.get('date_naissance'),
                'identifiant': data.get('identifiant'),
                'bulletin': data.get('choix_chiffre')  # Contient le choix chiffré
            })

        send_email(de_email, "Notification de dépouillement", "Un nouveau vote a été transmis pour dépouillement.")
        # Afficher la page avec les votes
        return render_template('comptage.html', votes=votes)

    except Exception as e:
        flash(f"Erreur lors de la récupération des votes : {str(e)}", 'danger')
        return render_template('comptage.html', votes=[])
