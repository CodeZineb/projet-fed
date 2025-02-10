import os
from flask import Flask, render_template
from app.routes.votant import votant_bp
from app.routes.comptage import comptage_bp
from app.routes.depouillement import depouillement_bp

app = Flask(
    __name__, 
    template_folder=os.path.join(os.path.dirname(__file__), "app", "templates")
)
app.secret_key = 'votre_cle_secrete'  # Nécessaire pour `flash`

# Enregistrer les blueprints
app.register_blueprint(votant_bp)
app.register_blueprint(comptage_bp)
app.register_blueprint(depouillement_bp)

@app.route("/")
def home():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)
