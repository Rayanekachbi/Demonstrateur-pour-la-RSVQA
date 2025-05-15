import unittest
from api import app, find_answer_by_question_id

class TestAnswerAPI(unittest.TestCase):

    def setUp(self):
        # Crée un client Flask pour simuler les requêtes HTTP
        self.client = app.test_client()

    # Test GET avec question_id valide (peut retourner 200 ou 404)
    def test_get_answer_get_valid(self):
        response = self.client.get('/get_answer/Low_Resolution/LR_split_train_answers?question_id=0')

        # Vérifie que le statut est 200 (trouvé) ou 404 (non trouvé)
        self.assertIn(response.status_code, [200, 404])

        # Si réponse trouvée, on vérifie les champs
        if response.status_code == 200:
            data = response.get_json()
            # Vérifie que la clé "question_id" est dans la réponse
            self.assertIn("question_id", data)
            # Vérifie que la clé "answer" est dans la réponse
            self.assertIn("answer", data)

    # Test GET sans fournir question_id (doit retourner 400)
    def test_get_answer_get_missing_param(self):
        response = self.client.get('/get_answer/Low_Resolution/LR_split_train_answers')
        # Vérifie que l'erreur est bien détectée (code 400)
        self.assertEqual(response.status_code, 400)
        # Vérifie que le message d'erreur est dans la réponse
        self.assertIn("error", response.get_json())

    # Test POST avec un JSON vide (doit retourner 400)
    def test_get_answer_post_missing(self):
        response = self.client.post('/get_answer/Low_Resolution/LR_split_train_answers', json={})
        # Vérifie que l'erreur est bien détectée (code 400)
        self.assertEqual(response.status_code, 400)
        # Vérifie que le message d'erreur est présent
        self.assertIn("error", response.get_json())

    # Test POST avec question_id valide (peut retourner 200 ou 404)
    def test_get_answer_post_valid(self):
        response = self.client.post('/get_answer/Low_Resolution/LR_split_train_answers', json={"question_id": 0})
        # Vérifie que le statut est correct selon l'existence de la donnée
        self.assertIn(response.status_code, [200, 404])

        # Si la réponse est OK, on valide les champs retournés
        if response.status_code == 200:
            data = response.get_json()
            # Vérifie la présence de "question_id"
            self.assertIn("question_id", data)
            # Vérifie la présence de "answer"
            self.assertIn("answer", data)

    # Test GET avec un dataset inexistant (doit retourner 404)
    def test_get_answer_invalid_dataset(self):
        response = self.client.get('/get_answer/Fake_dataset/fake_answers?question_id=0')
        # Vérifie que l'erreur 404 est bien retournée
        self.assertEqual(response.status_code, 404)
        # Vérifie la présence du message d'erreur dans la réponse
        self.assertIn("error", response.get_json())

    # Test unitaire direct de la fonction find_answer_by_question_id
    def test_find_answer_by_question_id(self):
        from api import DATA_CACHE

        # Injection manuelle de données fictives dans le cache
        dataset_key = "test_dir/test_file.json"
        DATA_CACHE[dataset_key] = [
            {"question_id": 1, "answer": "yes"},
            {"question_id": 2, "answer": "no"}
        ]

        # Vérifie que la bonne réponse est renvoyée pour question_id=1
        result = find_answer_by_question_id(dataset_key, 1)
        self.assertEqual(result, "yes")

        # Vérifie que None est renvoyé pour un question_id inexistant
        result_none = find_answer_by_question_id(dataset_key, 99)
        self.assertIsNone(result_none)
