import smtplib
from email.mime.text import MIMEText

# Détails du compte Gmail
email = "nouhaila.boud1708@gmail.com"
password = "voibaztradhbpqrj"

# Créer un email
def send_email(destinataire, sujet, contenu):
    try:
        msg = MIMEText(contenu)
        msg['From'] = email
        msg['To'] = destinataire
        msg['Subject'] = sujet

        # Configurer le serveur SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(email, destinataire, msg.as_string())
            print(f"Email envoyé à {destinataire} avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
