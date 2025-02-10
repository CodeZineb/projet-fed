from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importer et enregistrer le blueprint votant
    from app.routes.votant import votant_bp
    app.register_blueprint(votant_bp)

    return app
