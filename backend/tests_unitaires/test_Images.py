import unittest
from api import app

# Définition de la classe de tests pour l'endpoint /api/dataset-images/<dataset_name>
class TestDatasetImagesAPI(unittest.TestCase):

    def setUp(self):
        # Crée un client de test Flask pour simuler les requêtes HTTP
        self.client = app.test_client()

    def test_get_dataset_images_valid(self):
        # Ce test vérifie que l'API retourne bien la liste des images
        # pour un dataset valide existant (ex. "Low_Resolution").

        # On envoie une requête GET avec un nom de dataset valide
        response = self.client.get('/api/dataset-images/Low_Resolution')

        # Le code de réponse doit être 200 si le dataset existe
        self.assertEqual(response.status_code, 200)

        # On récupère les données JSON de la réponse
        data = response.get_json()

        # La réponse doit contenir les clés attendues
        self.assertIn("dataset", data)     # Le nom du dataset
        self.assertIn("images", data)      # La liste des images
        self.assertIn("count", data)       # Le nombre d’images

        # Vérifie que "images" est une liste
        self.assertIsInstance(data["images"], list)

    def test_get_dataset_images_invalid(self):
        # Ce test vérifie que l'API gère correctement un nom de dataset inexistant

        # On envoie une requête GET avec un nom de dataset qui n'existe pas
        response = self.client.get('/api/dataset-images/Dataset_Inexistant')

        # Le code de réponse doit être 404 (non trouvé)
        self.assertEqual(response.status_code, 404)

        # La réponse doit contenir une clé "error"
        self.assertIn("error", response.get_json())

# Définition de la classe de tests pour l'endpoint /api/images/<dataset_name>/<filename>
class TestGetImage(unittest.TestCase):

    def setUp(self):
        # Crée un client de test Flask pour simuler les requêtes HTTP
        self.client = app.test_client()

    def test_get_image_valid(self):
        # Ce test vérifie que l'API retourne bien une image existante dans un dataset

        # Requête GET vers une image valide du dataset "Low_Resolution"
        response = self.client.get('/api/images/Low_Resolution/0.tif')

        # Le code de statut doit être 200 si l'image est trouvée et servie correctement
        self.assertEqual(response.status_code, 200)

        # Vérifie que le type (.tif,.png etc...) de la réponse est une image PNG (conversion réussie)
        self.assertEqual(response.content_type, 'image/png')

    def test_get_image_invalid(self):
        # Ce test vérifie que l'API retourne une erreur 404 pour une image qui n'existe pas

        # On fait une requête vers une image inexistante
        response = self.client.get('/api/images/Low_Resolution/image_inexistante.tif')

        # Le code de réponse doit être 404
        self.assertEqual(response.status_code, 404)

        # La réponse doit contenir une clé "error" expliquant le problème
        self.assertIn("error", response.get_json())