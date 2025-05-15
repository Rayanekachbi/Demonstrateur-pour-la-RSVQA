# Tests Unitaires – API Flask RSVQA

Ce dossier contient l'ensemble des **tests unitaires** pour l'API.

## Structure des tests

- `test_Answer.py` – pour les fonctions :
    - `find_answer_by_question_id`
        - Vérifier la recherche d'une réponse avec un `question_id` valide dans un dataset.
        - Vérifier le cas où aucun `answer` n'est trouvé pour un `question_id` donné.
        - Vérifier que la fonction renvoie `None` si le dataset n'existe pas dans le cache.

    - `get_answer (GET)`
        - Vérifier le cas où `question_id` est fourni et l'`answer` est trouvé.
        - Vérifier le cas où `question_id` est manquant et une erreur 400 est retournée.
        - Vérifier le cas où le dataset demandé n'existe pas et une erreur 404 est retournée.
        - Vérifier le comportement avec un `question_id` valide et s'il renvoie le bon format de réponse (avec `question_id` et `answer`).

    - `get_answer (POST)`
        - Vérifier le cas où le body de la requête est vide et retourne une erreur 400.
        - Vérifier le cas où le `question_id` est valide dans le body de la requête et l'`answer` est trouvé.
        - Vérifier le cas où le `question_id` dans la requête est invalide et retourne une erreur 404.
        - Vérifier le comportement avec un body de requête valide, renvoyant la bonne réponse avec `question_id` et `answer`.

                                        
- `test_Custom_model.py` – pour les fonctions :
    - `ask_custom_question (POST)`
        - Vérifier que l'endpoint retourne un code de statut 200 lorsque toutes les données nécessaires sont fournies (question, image_id, dataset).
        - Vérifier que la réponse contient bien les champs `answer_vqa` et `answer_vilt` (modèles VQA et ViLT).
        - Vérifier que l'API retourne une erreur 400 lorsqu'aucune donnée n'est fournie dans la requête.
        - Vérifier que la réponse contient un champ `error` expliquant l'absence de données dans la requête.


- `test_Dataset_api.py` – pour les fonctions :
    - `get_all_datasets (GET)`
        - Vérifier que l'endpoint retourne un code de statut 200 lorsque la requête est réussie.
        - Vérifier que la réponse contient bien une liste de datasets.
        - Vérifier que chaque dataset contient les champs attendus : `id`, `name`, `num_images`, `owner`, `modes`, `image`.
        
    - `get_all_data_valid (GET)`
        - Vérifier que l'API retourne des données valides pour le dataset "Low_Resolution" et les images associées.
        - Vérifier que les images sont bien présentes dans la réponse et qu'il y a au moins une image.

    - `get_all_questions_valid (GET)`
        - Vérifier que l'API retourne toutes les questions pour le dataset "Low_Resolution".
        - Vérifier que la réponse contient bien une liste de questions.

    - `get_all_answers_valid (GET)`
        - Vérifier que l'API retourne toutes les réponses pour le dataset "Low_Resolution".
        - Vérifier que la réponse contient bien une liste de réponses.

    - `get_all_data_invalid_dataset (GET)`
        - Vérifier que l'API retourne une erreur 404 lorsque le dataset n'existe pas.
        - Vérifier que le message d'erreur contient "Dataset non trouvé".

    - `get_all_data_invalid_file_type (GET)`
        - Vérifier que l'API retourne une erreur 400 lorsque le type de fichier demandé est invalide.
        - Vérifier que le message d'erreur contient "Type de fichier non supporté".

    - `get_all_data_invalid_json (GET)`
        - Vérifier que l'API retourne une erreur 500 lorsqu'un fichier JSON mal formé est rencontré.
        - Utiliser `patch` pour simuler une erreur de décodage JSON et tester le bon comportement de l'API.
        - Vérifier que le message d'erreur contient "Erreur de décodage JSON".


- `test_Dataset_loading.py` – pour les fonctions :
    - `test_cache_is_populated`
        - Vérifier que `DATA_CACHE` est bien un dictionnaire.
        - Vérifier que `DATA_CACHE` n'est pas vide après le chargement des datasets.

    - `test_load_all_datasets_structure`
        - Vérifier que le dictionnaire `DATA_CACHE` contient les bonnes clés pour les datasets chargés.
        - Vérifier que les fichiers comme "Low_Resolution/LR_split_test_images.json" et "High_Resolution/USGS_split_train_questions.json" sont bien présents dans le cache.


- `test_Dataset_uploading.py` – pour les fonctions :
    - `test_upload_dataset_success`
        - Vérifier que le téléchargement du dataset fonctionne correctement avec des fichiers valides.
        - Vérifier que la réponse HTTP est 200 et que le message de succès est renvoyé avec le nom du dataset.

    - `test_upload_dataset_no_files`
        - Vérifier le comportement de l'API lorsqu'aucun fichier n'est reçu.
        - Vérifier que l'API retourne une erreur 400 et le message approprié.


- `test_Images.py` – pour les fonctions :
    - `test_get_dataset_images_valid`
        - Vérifier que l'API retourne bien la liste des images pour un dataset valide existant.
        - Vérifier que la réponse contient les informations attendues : "dataset", "images", et "count".
        - Vérifier que "images" est bien une liste.

    - `test_get_dataset_images_invalid`
        - Vérifier que l'API retourne une erreur 404 pour un dataset inexistant.
        - Vérifier que la réponse contient un message d'erreur.

    - `test_get_image_valid`
        - Vérifier que l'API retourne correctement une image existante dans un dataset.
        - Vérifier que le type de la réponse est bien une image PNG.

    - `test_get_image_invalid`
        - Vérifier que l'API retourne une erreur 404 pour une image inexistante.
        - Vérifier que la réponse contient un message d'erreur expliquant le problème.


## Lancer tous les tests

Depuis la racine le backend en ayant son environnement activé :
    python -m unittest discover tests

pour tester fichier par fichier :
    python -m unittest tests_unitaires.nomdufichier

exemple 
    python -m unittest tests_unitaires.test_Dataset_api

