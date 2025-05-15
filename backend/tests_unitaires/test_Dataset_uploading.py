import unittest
from api import app
from io import BytesIO

# Définition de la classe de test pour le téléchargement de datasets
class TestUploadDataset(unittest.TestCase):

    def setUp(self):
        # Initialisation du client Flask avant chaque test
        self.client = app.test_client()

    def test_upload_dataset_success(self):
        # Ce test vérifie que l'upload fonctionne correctement avec des fichiers valides

        # Simulation d'un fichier JSON nommé 'Low_Resolution/sample.json' avec un contenu factice
        data = {
            'files': [
                (BytesIO(b'{"test": "value"}'), 'Low_Resolution/sample.json')
            ]
        }

        # Envoi d'une requête POST avec le fichier
        response = self.client.post(
            '/api/upload-dataset',
            content_type='multipart/form-data',
            data=data
        )

        # Vérifie que la réponse est un succès HTTP 200
        self.assertEqual(response.status_code, 200)

        # Vérifie que le message de succès est présent dans la réponse
        self.assertIn("Dataset 'Low_Resolution' importé avec succès", response.get_json().get("message", ""))


    def test_upload_dataset_no_files(self):
        # Ce test vérifie la gestion d'une requête sans données
        response = self.client.post('/api/upload-dataset', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Aucun fichier reçu", response.get_json().get("error", ""))



