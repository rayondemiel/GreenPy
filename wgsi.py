from GreenPy.app import config_app
import os

app = config_app("production")

# Vérifiez si ce fichier est exécuté par Gunicorn
if __name__ == "__main__":
    # Obtenez le port de l'environnement, ou utilisez 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    
    # Exécutez l'application Flask via Gunicorn
    from gunicorn.app.base import Application

    class StandaloneApplication(Application):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 4  # Vous pouvez ajuster le nombre de travailleurs selon vos besoins
    }

    StandaloneApplication(app, options).run()
