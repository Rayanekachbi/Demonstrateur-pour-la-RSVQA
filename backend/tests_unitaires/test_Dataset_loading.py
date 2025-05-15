import unittest
from api import DATA_CACHE, load_all_datasets

class TestDatasetLoading(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Charge les datasets avant tous les tests
        load_all_datasets()

    def test_cache_is_populated(self):
        #Test pour vérifier que DATA_CACHE est bien un dictionnaire et qu'il n'est pas vide
        #après l'appel à load_all_datasets()
        self.assertIsInstance(DATA_CACHE, dict)
        self.assertGreater(len(DATA_CACHE), 0)

    def test_load_all_datasets_structure(self):
        #Test pour vérifier que le dictionnaire DATA_CACHE contient les bonnes keys
        #On s'assure que ces keys sont bien présentes dans le cache
        self.assertIn("Low_Resolution/LR_split_test_images.json", DATA_CACHE)
        self.assertIn("High_Resolution/USGS_split_train_questions.json", DATA_CACHE)
