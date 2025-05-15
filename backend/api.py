from flask import Flask, request, jsonify, send_file
import torch 
from torchvision import transforms
from PIL import Image
import json
import os
from io import BytesIO
from  flask_cors import CORS
from pathlib import Path

#Importations pour modèle 
from Model_L2 import VQAModel, VocabEncoder
from transformers import DistilBertTokenizer, ViltProcessor, ViltForQuestionAnswering

app = Flask(__name__)
CORS(app)


# Initialisation du modele RSVQA
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = VQAModel().to(device) #Création du modele et envoie sur le GPU ou le CPU
checkpoint = torch.load("./BigModel_30.tar", map_location=device) #Charhe le poid du modèle
model.load_state_dict(checkpoint['model_state_dict']) # Charge les poids du modèle
model.eval() #place le modele en mode évaluation

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased") #initialise le tokenizer à partir du modele pré-entrainé.

# Initialisation du modèle ViLT
vilt_processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
vilt_model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa").to(device)
vilt_model.eval()


# Chemin vers le dossier contenant les datasets
DATASETS_BASE_DIR = './datasets'
# Gestion des datasets en cache
DATA_CACHE = {}


###  PARTIE DATASET-IMAGES


#lister les datasets qui se trouvent dans le dossier datasets 
@app.route('/datasets', methods=['GET'])
def get_all_dataset():
    base_path = answers_path = DATASETS_BASE_DIR
    datasets = []
    # Boucle sur les sous-dossiers (un par dataset)
    for idx, dataset_name in enumerate(os.listdir(base_path), start=1):
        dataset_dir = os.path.join(base_path, dataset_name, "Images_LR")
        
        image_file = None
        if os.path.isdir(dataset_dir):
            tif_images = [img for img in os.listdir(dataset_dir) if img.endswith('.tif')]
            if tif_images:
                image_file = f"{dataset_name}/Images_LR/{tif_images[0]}"  # prend la première image
        datasets.append({
            "id": idx,
            "name": dataset_name,
            "num_images": len(tif_images) if image_file else 0,
            "owner": "User A",  
            "modes": "Train, Test",  
            "image": image_file
        })
    return jsonify(datasets)

#GET : récupérer tout le contenu d'un dataset spécifique
@app.route('/api/get_all/<dataset_name>/<file_type>', methods=['GET'])
def get_all_data(dataset_name, file_type):
    """
    Fonction unifiée pour récupérer:
    - Les images (file_type='images')
    - Les questions (file_type='all_questions')
    - Les réponses (file_type='all_answers')
    """
    dataset_path = os.path.join(DATASETS_BASE_DIR, dataset_name)
    
    if not os.path.exists(dataset_path):
        return jsonify({"error": "Dataset non trouvé"}), 404
    # Pour les images
    if file_type == 'images':
        images_dir = os.path.join(dataset_path, "Images_LR")
        valid_extensions = ('.tif', '.tiff', '.png', '.jpg', '.jpeg')
        try:
            images = [
                img for img in os.listdir(images_dir)
                if img.lower().endswith(valid_extensions)
            ]
            return jsonify({
                "dataset": dataset_name,
                "images": images,
                "count": len(images)
            })
        except FileNotFoundError:
            return jsonify({"error": "Dossier Images_LR non trouvé"}), 404
    # Pour les fichiers JSON (questions/réponses)
    elif file_type in ['all_questions', 'all_answers']:
        file_path = os.path.join(dataset_path, f"{file_type}.json")
        
        if not os.path.isfile(file_path):
            return jsonify({"error": f"Fichier {file_type}.json non trouvé"}), 404
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return jsonify(data)
        except json.JSONDecodeError:
            return jsonify({"error": "Erreur de décodage JSON"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Type de fichier non supporté"}), 400

#récupérer les images d'un dataset spécificque
@app.route('/api/dataset-images/<dataset_name>')
def get_dataset_images(dataset_name):
    # Chemin vers le dossier du dataset
    dataset_path = os.path.join(DATASETS_BASE_DIR, dataset_name)
    
    # Vérifie que le dataset existe
    if not os.path.exists(dataset_path):
        return jsonify({"error": "Dataset non trouvé"}), 404
    
    # Chemin vers le dossier des images
    images_dir = os.path.join(dataset_path, "Images_LR")
    
    # Liste les fichiers images (ajustez les extensions si nécessaire)
    valid_extensions = ('.tif', '.tiff', '.png', '.jpg', '.jpeg')
    try:
        images = [
            img for img in os.listdir(images_dir)
            if img.lower().endswith(valid_extensions)
        ]
    except FileNotFoundError:
        return jsonify({"error": "Dossier Images_LR non trouvé"}), 404
    return jsonify({
        "dataset": dataset_name,
        "images": images,
        "count": len(images)
    })

#fonction pour charger tous les datasets en mémoire
def load_all_datasets():

    """Charge tous les fichiers JSON en mémoire, récursivement."""
    global DATA_CACHE
    if not os.path.exists(DATASETS_BASE_DIR):
        print(f"Dossier {DATASETS_BASE_DIR} introuvable")
        return
    for root, dirs, files in os.walk(DATASETS_BASE_DIR):
        for filename in files:
            if filename.endswith('.json'):
                filepath = os.path.join(root, filename)
                # Création d'une clé relative 
                relative_path = os.path.relpath(filepath, DATASETS_BASE_DIR).replace("\\", "/")  # pour Windows
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if isinstance(data, dict) and "answers" in data:
                            DATA_CACHE[relative_path] = data["answers"]
                        elif isinstance(data, dict) and "questions" in data:
                            DATA_CACHE[relative_path] = data["questions"]
                        elif isinstance(data, dict) and "images" in data:
                            DATA_CACHE[relative_path] = data["images"]
                        else:
                            DATA_CACHE[relative_path] = data
                        print(f" {relative_path} a été chargé.")
                except json.JSONDecodeError:
                    print(f"Erreur JSON dans {relative_path}")
                except Exception as e:
                    print(f"Erreur lors du chargement de {relative_path}: {e}")

#récupérer une image spécificque d'un dataset 
@app.route('/api/images/<dataset_name>/<filename>', methods=['GET'])
def get_image(dataset_name, filename):
    image_path = os.path.join(DATASETS_BASE_DIR, dataset_name, "Images_LR", filename)

    if not os.path.isfile(image_path):
        return jsonify({"error": "Image non trouvée"}), 404

    try:
        img = Image.open(image_path).convert("RGB")  # Converti pour la compatibilité avec le navigateur
        img_io = BytesIO()
        img.save(img_io, format='PNG')  # Sauvegarde dans le buffer au format PNG
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
#Charger tous les datasets au démarrage
load_all_datasets()

#upload un nouveau dataset
@app.route('/api/upload-dataset', methods=['POST'])
def upload_dataset():
    if 'files' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Liste vide"}), 400
    first_file = files[0]
    base_path_parts = first_file.filename.split('/')
    dataset_name = base_path_parts[0]
    dataset_path = os.path.join("datasets", dataset_name)
    for file in files:
        file_path_parts = file.filename.split('/')
        if len(file_path_parts) < 2:
            continue
        relative_path = os.path.join(*file_path_parts[1:])
        save_path = os.path.join(dataset_path, relative_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
    return jsonify({"message": f"Dataset '{dataset_name}' importé avec succès"}), 200


###   PARTIE QUESTION-REPONSE 


# Fonction pour trouver un answer par question_id
def find_answer_by_question_id(dataset_key, question_id):
    if dataset_key not in DATA_CACHE:
        return None
    for entry in DATA_CACHE[dataset_key]:
        if isinstance(entry, dict) and entry.get("question_id") == question_id:
            return entry.get("answer")
    return None

# GET : récupérer answer avec question_id (dans un dataset spécifique)
@app.route('/get_answer/<dataset_dir>/<dataset>', methods=['GET'])
def get_answer(dataset_dir, dataset):
    dataset_key = f"{dataset_dir}/{dataset}.json"
    question_id = request.args.get('question_id', type=int)
    
    if dataset_key not in DATA_CACHE:
        return jsonify({"error": f"No dataset found for {dataset} in {dataset_dir}"}), 404

    if question_id is None:
        return jsonify({"error": "Missing question_id parameter"}), 400

    answer = find_answer_by_question_id(dataset_key, question_id)
    if answer is None:
        return jsonify({"error": "No answer found for this question_id"}), 404

    return jsonify({"question_id": question_id, "answer": answer})

# POST : récupérer answer avec question_id (dans un dataset spécifique)
@app.route('/get_answer/<dataset_dir>/<dataset>', methods=['POST'])
def post_answer(dataset_dir, dataset):
    dataset_key = f"{dataset_dir}/{dataset}.json"
    data = request.get_json()

    if dataset_key not in DATA_CACHE:
        return jsonify({"error": f"No dataset found for {dataset} in {dataset_dir}"}), 404

    if not data or "question_id" not in data:
        return jsonify({"error": "Missing question_id in request body"}), 400

    question_id = data["question_id"]
    answer = find_answer_by_question_id(dataset_key, question_id)

    if answer is None:
        return jsonify({"error": "No answer found for this question_id"}), 404

    return jsonify({"question_id": question_id, "answer": answer})

# POST : envoyer une ou plusieurs questions et la photo au modèle et récupérer la réponse.
@app.route('/ask_custom_question', methods=['POST'])
def ask_custom_question():
    data = request.get_json()
    questions = data.get("questions")
    question_str = data.get("question")
    image_id = data.get("image_id")
    dataset = data.get("dataset")

    # Vérifie la présence de l'image_id (attention : 0 est un id valide)
    if image_id is None:
        return jsonify({"error": "image_id is missing"}), 400

    try:
        # Chargement de l'image
        image_path = os.path.join(DATASETS_BASE_DIR, dataset, "Images_LR", f"{image_id}.tif")
        img = Image.open(image_path)

        # Prétraitement image pour VQA model
        img_tensor_vqa = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])(img).unsqueeze(0).to(device)

        # Vocabulaire dynamique pour le dataset utilisé
        answers_path = os.path.join(DATASETS_BASE_DIR, dataset, "all_answers.json")
        encoder_answers = VocabEncoder(answers_path, questions=False)

        # Cas : plusieurs questions
        if questions:
            results = []
            for q in questions:
                # Inference avec VQAModel
                question_tensor = tokenizer(q, return_tensors="pt", padding='max_length', max_length=36, add_special_tokens=True).to(device)
                with torch.no_grad():
                    output_vqa = model(img_tensor_vqa, {key: val.to(device) for key, val in question_tensor.items()})
                    pred_vqa = torch.max(output_vqa.data, dim=1)
                    decoded_vqa = encoder_answers.decode(pred_vqa.indices.tolist())
                # Inference avec ViLT
                inputs_vilt = vilt_processor(img, q, return_tensors="pt").to(device)
                with torch.no_grad():
                    outputs_vilt = vilt_model(**inputs_vilt)
                    pred_vilt = outputs_vilt.logits.argmax(-1).item()
                    decoded_vilt = vilt_model.config.id2label[pred_vilt]
                results.append({
                    "question": q,
                    "answer_vqa": decoded_vqa,
                    "answer_vilt": decoded_vilt
                })
            return jsonify({"answers": results})
        # Cas : une seule question
        elif question_str:
            question_tensor = tokenizer(question_str, return_tensors="pt", padding='max_length', max_length=36, add_special_tokens=True).to(device)
            with torch.no_grad():
                output_vqa = model(img_tensor_vqa, {key: val.to(device) for key, val in question_tensor.items()})
                pred_vqa = torch.max(output_vqa.data, dim=1)
                decoded_vqa = encoder_answers.decode(pred_vqa.indices.tolist())[0]

            inputs_vilt = vilt_processor(img, question_str, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs_vilt = vilt_model(**inputs_vilt)
                pred_vilt = outputs_vilt.logits.argmax(-1).item()
                decoded_vilt = vilt_model.config.id2label[pred_vilt]

            return jsonify({
                "answer_vqa": decoded_vqa,
                "answer_vilt": decoded_vilt
            })

        else:
            return jsonify({"error": "question or questions field is required"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)



#ceci devait servir pour les datasets qui n'ont pas une structure similaire pour le stockage de l'image
# backend/datasets/<datasetname>/Images_LR/<image>.tif
#ça fonctionne avec les chemins menant à l'image

#images_by_dataset = {}
#for root, dirs, files in os.walk(DATASETS_BASE_DIR):
#    tif_images = [f for f in files if f.endswith('.tif')]
#    if tif_images:
#        # Déduire le dataset à partir du chemin relatif
#        relative_root = os.path.relpath(root, DATASETS_BASE_DIR).replace("\\", "/")  # Windows
#        dataset_name = relative_root.split('/')[0]  # Premier dossier après datasets/
#
#        if dataset_name not in images_by_dataset:
#            images_by_dataset[dataset_name] = []
#
#        for img in tif_images:
#            images_by_dataset[dataset_name].append(os.path.join(relative_root, img))  # stocke chemin relatif
#
### Servir une image spécifique
#@app.route('/api/images/<path:image_path>', methods=['GET'])
#def get_image(image_path):
#    image_path = image_path.replace("\\", "/")
#    full_path = os.path.join(DATASETS_BASE_DIR, image_path)
#
#    if not os.path.isfile(full_path):
#        return jsonify({"error": "Image non trouvée"}), 404
#
#    try:
#        with Image.open(full_path) as img:
#            img_io = BytesIO()
#            img.convert('RGB').save(img_io, 'PNG')
#            img_io.seek(0)
#            return send_file(img_io, mimetype='image/png')
#    except Exception as e:
#        return jsonify({"error": str(e)}), 500