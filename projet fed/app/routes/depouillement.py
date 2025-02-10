from flask import Blueprint, render_template, flash
from app.firebase_config import db
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

# Créer un blueprint pour le centre de dépouillement
depouillement_bp = Blueprint('depouillement', __name__, url_prefix='/depouillement')

def load_private_key(private_key_pem):
    """Charge une clé privée à partir d'une chaîne PEM."""
    return serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )

@depouillement_bp.route('/', methods=['GET'])
def depouillement():
    try:
        # Récupérer les votes chiffrés depuis Firestore
        votes_ref = db.collection('votes')
        votes_docs = votes_ref.stream()

        # Préparer les résultats
        results = []
        for doc in votes_docs:
            data = doc.to_dict()

            identifiant = data.get('identifiant')
            bulletin_chiffre = data.get('choix_chiffre')  # Bulletin chiffré récupéré
            private_key_pem = data.get('private_key')  # Clé privée du votant
            bulletin_dechiffre = None
            statut = "Validé"

            try:
                # Charger la clé privée
                private_key = load_private_key(private_key_pem)

                # Déchiffrer le bulletin
                bulletin_dechiffre = private_key.decrypt(
                    base64.b64decode(bulletin_chiffre),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('utf-8')
            except Exception as e:
                statut = f"Erreur: {str(e)}"

            # Ajouter le résultat à la liste
            results.append({
                'identifiant': identifiant,
                'bulletin': bulletin_dechiffre if bulletin_dechiffre else "Échec déchiffrement",
                'statut': statut
            })

        # Afficher les résultats dans le template
        return render_template('depouillement.html', results=results)

    except Exception as e:
        flash(f"Erreur lors du traitement des votes : {str(e)}", 'danger')
        return render_template('depouillement.html', results=[])
