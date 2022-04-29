from GreenPy.modeles.utilisateurs import User
from test_base import Base

class TestUser(Base):
    def test_creation(self):
        with self.app.app_context():
            statut, utilisateur = User.creer("joh", "johanna.johanna@enc-sorbonne.fr", "Johanna", "azerty85L#")
            query = User.query.filter(User.user_email == "johanna.johanna@enc-sorbonne.fr").first()
        self.assertEqual(query.user_nom, "Johanna")
        self.assertEqual(query.user_login, "joh")
        self.assertNotEqual(query.user_password, "azerty85L#")
        self.assertTrue(statut)

    def test_login_et_creation(self):
        with self.app.app_context():
            statut, cree = User.creer("joh", "johanna.johanna@enc-sorbonne.fr", "Johanna", "azerty85L#")
            connecte = User.identification("joh", "azerty85#")
        self.assertEqual(cree, connecte)
        self.assertTrue(statut)