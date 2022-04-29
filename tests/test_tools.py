import os.path

from GreenPy.routes.map import carte_native, carte, resultat_carte
from GreenPy.app import templates
from test_base import Base

class TestMap(Base, carte):
    def test_creation_map(self):
        with self.app.app_context():
            if carte:
                assertTrue(os.path.exists(os.path.join(templates, 'partials/map.html'))),
