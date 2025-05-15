import unittest
from api import app
from unittest.mock import patch
import json

class TestGetAllDataset(unittest.TestCase):
     
    def setUp(self):
        # Créer un client de test Flask pour simuler des requêtes HTTP
        self.client = app.test_client()

    def test_get_all_datasets(self):
        # Envoi d'une requête GET pour récupérer tous les datasets
        response = self.client.get('/datasets')
        
        # Vérifie que la réponse a un code de statut 200 (succès)
        self.assertEqual(response.status_code, 200)
        
        # Récupère les données JSON dans la réponse
        data = response.get_json()

        # Vérifie que la réponse est une liste
        self.assertIsInstance(data, list)
        
        # Vérifie que chaque dataset dans la réponse contient les bons champs
        for dataset in data:
            self.assertIn("id", dataset)
            self.assertIn("name", dataset)
            self.assertIn("num_images", dataset)
            self.assertIn("owner", dataset)
            self.assertIn("modes", dataset)
            self.assertIn("image", dataset)

class TestGetAllData(unittest.TestCase):
    
    def setUp(self):
        # Créer un client de test Flask pour simuler des requêtes HTTP
        self.client = app.test_client()

    def test_get_all_data_valid(self):
        # Test pour récupérer les images du dataset "Low_Resolution"
        response = self.client.get('/api/get_all/Low_Resolution/images')
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que la réponse contient des images et qu'il y a bien des fichiers d'images
        data = response.get_json()
        self.assertIn("dataset", data)
        self.assertIn("images", data)
        self.assertGreater(len(data["images"]), 0)  # S'il y a des images

    def test_get_all_questions_valid(self):
        # Test pour récupérer toutes les questions du dataset "Low_Resolution"
        response = self.client.get('/api/get_all/Low_Resolution/all_questions')
        self.assertEqual(response.status_code, 200)

        # Vérifie que la réponse contient des questions
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("questions", data)
        self.assertIsInstance(data["questions"], list)

    def test_get_all_answers_valid(self):
        # Test pour récupérer toutes les réponses du dataset "Low_Resolution"
        response = self.client.get('/api/get_all/Low_Resolution/all_answers')
        self.assertEqual(response.status_code, 200)

        # Vérifie que la réponse contient des réponses
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn("answers", data)
        self.assertIsInstance(data["answers"], list)

    def test_get_all_data_invalid_dataset(self):
        # Test pour vérifier le cas où le dataset demandé n'existe pas
        response = self.client.get('/api/get_all/non_existent_dataset/all_questions')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Dataset non trouvé", response.get_json().get("error", ""))

    def test_get_all_data_invalid_file_type(self):
        # Test pour vérifier le cas où le type de fichier demandé n'est pas valide
        response = self.client.get('/api/get_all/Low_Resolution/non_existent_file_type')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Type de fichier non supporté", response.get_json().get("error", ""))


    def test_get_all_data_invalid_json(self): 
        #Test pour vérifier le comportement de l'API quand un fichier JSON est invalide (mal formé).
        #On simule ici une erreur de décodage JSON, sans avoir besoin d'un vrai fichier corrompu sur le disque.

        # Utilisation de 'patch' pour remplacer temporairement la fonction open()
        # Cela permet de simuler l'ouverture d'un fichier sans réellement accéder au disque.
        # 'create=True' est utilisé pour permettre de patcher même si 'open' n'a pas été explicitement importée.
        with patch("builtins.open", create=True) as mock_open:
            
            # Configuration du "faux fichier" pour que lorsqu'on lit son contenu, il renvoie une chaîne invalide ("invalid_json")
            # Cela simule un fichier JSON corrompu qui ne peut pas être interprété correctement par json.load().
            # mock_open : c’est la version simulée de open(). On peut lui dire quoi renvoyer quand on lit un fichier 
            # Ici, on lui dit de renvoyer "invalid_json" comme contenu.
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid_json"

            # Patch signifie remplacer temporairement un objet, une fonction ou une méthode par une version simulée (appelée un mock) 
            # pendant l’exécution d’un test.
            # Patch de la fonction json.load pour simuler une exception JSONDecodeError lorsque l'API essaie de charger le fichier.
            # Cela permet de tester si l'API gère correctement cette erreur sans planter.
            with patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "invalid_json", 0)):

                # On fait un appel GET vers l'API comme si on voulait récupérer un fichier JSON cassé
                response = self.client.get('/api/get_all/Low_Resolution/all_answers')

                # On s'attend à ce que le serveur renvoie une erreur 500 (erreur interne du serveur)
                # car il ne peut pas traiter correctement le fichier JSON invalide.
                self.assertEqual(response.status_code, 500)

                # On vérifie que le message d'erreur retourné mentionne bien une erreur de décodage JSON.
                # Cela garantit que l'API informe correctement de la nature de l'erreur.
                self.assertIn("Erreur de décodage JSON", response.get_json().get("error", ""))
