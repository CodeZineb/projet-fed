from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.firebase_config import db  # Import Firestore
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from app.email_utils import send_email

co_email = "nouhaila.boudad@uit.ac.ma"  # Adresse email de CO

# Créer un blueprint
votant_bp = Blueprint('votant', __name__, url_prefix='/votant')

@votant_bp.route('/', methods=['GET', 'POST'])
def votant():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naissance = request.form.get('date_naissance')
        identifiant = request.form.get('identifiant')
        choix = request.form.get('choix')

        if not (nom and prenom and date_naissance and identifiant and choix):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('votant.html')

        try:
            # Vérifier si un vote avec cet identifiant existe déjà
            votes_ref = db.collection('votes')
            existing_votes = votes_ref.where('identifiant', '==', identifiant).stream()

            if any(existing_votes):  # Si un identifiant existe déjà
                flash(f"L'identifiant {identifiant} a déjà voté.", 'danger')
                return render_template('votant.html')

            # Générer une paire de clés publique/privée pour le votant
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            public_key = private_key.public_key()

            # Chiffrer le choix avec la clé publique (par exemple, pour le centre de dépouillement)
            encrypted_choice = public_key.encrypt(
                choix.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Convertir les clés en format lisible (base64) pour les stocker
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')

            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')

            # Sauvegarder les données dans Firestore
            db.collection('votes').add({
                'nom': nom,
                'prenom': prenom,
                'date_naissance': date_naissance,
                'identifiant': identifiant,
                'choix_chiffre': base64.b64encode(encrypted_choice).decode('utf-8'),
                'public_key': public_key_pem,
                'private_key': private_key_pem
            })

            flash('Votre vote a été enregistré avec succès.', 'success')
            send_email(co_email, "Notification de vote", f"Un nouveau vote a été soumis par {nom}.")
            return redirect(url_for('votant.votant'))

        except Exception as e:
            flash(f"Une erreur s'est produite : {str(e)}", 'danger')

    return render_template('votant.html')
