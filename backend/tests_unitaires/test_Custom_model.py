import unittest
from api import app  

# Définition de la classe de tests pour l'endpoint /ask_custom_question
class TestCustomQuestion(unittest.TestCase):

    def setUp(self):
        #créer un client de test Flask pour simuler des reuettes HTTP
        #avant chaque test on execute la méthode setUp
        self.client = app.test_client()

    def test_custom_question_success(self):
        #vérification du bon fonctionnement de l'endpoint /ask_custom_question
        #quand toutes les données nécessaires sont fournies.

        # On simule une requête POST avec des données valides
        res = self.client.post('/ask_custom_question', json={
            "question": "Est-ce une zone agricole ?",
            "image_id": 1,
            "dataset": "Low_Resolution"
        })

        # si la requête a réussi, le code de statut doit être 200
        self.assertEqual(res.status_code, 200)

        # On récupère les données JSON de la réponse
        json_data = res.get_json()

        # On vérifie que la réponse contient bien les deux champs attendus
        self.assertIn("answer_vqa", json_data)   # Réponse générée par le modèle VQA
        self.assertIn("answer_vilt", json_data)  # Réponse générée par le modèle ViLT

    def test_custom_question_missing_data(self):
        #Ce test vérifie que l'API gère correctement les cas où les données sont absentes.
        
        # On envoie une requête POST vide
        res = self.client.post('/ask_custom_question', json={})

        # L'API devrait répondre avec une erreur 400 
        self.assertEqual(res.status_code, 400)

        # La réponse doit contenir un champ "error" expliquant le problème
        self.assertIn("error", res.get_json())
