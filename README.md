Scroll down for english version !
---

# Démonstrateur RSVQA – Projet L2V

**Encadrant :** Boussaid Hichem
**Catégorie :** Application scientifique
**Technologies :** Python,Flask, PyTorch, NumPy
**Mots-clés :** RSVQA, NLP, Deep Learning, Remote Sensing

---

## Contexte

La **Remote Sensing Visual Question Answering (RSVQA)** est un domaine de recherche à l’intersection de la **télédétection** et de l’**intelligence artificielle**. L’objectif est de permettre à un modèle de répondre, en **langage naturel**, à des questions portant sur des **images satellites ou aériennes**.

Les questions peuvent concerner :

* la détection d’objets,
* l’estimation de quantités,
* l’identification de terrains,
* les relations spatiales, etc.

Ce démonstrateur propose une **interface graphique** permettant d’utiliser un modèle RSVQA sur un ou plusieurs jeux de données publics.

---

## Fonctionnalités du projet

### 1. Sélection du dataset

* Choix d’un dataset prédéfini via une liste.
* Affichage des métadonnées : type de données, nombre d’images, etc.

### 2. Chargement d’images

* Chargement d’une liste d’images spécifiques au dataset sélectionné.
* Sélection et affichage de l’image.

### 3. Sélection ou création de questions

* Choix d’une question existante liée à l’image.
* Possibilité de saisir une question personnalisée via un champ texte.

### 4. Génération de la réponse

* Réponse générée par les modèles VQA et ViLT.

---

## Références

Lobry, S., Murray, J., Marcos, D., & Tuia, D. (2019).
*Visual Question Answering From Remote Sensing Images*. IGARSS 2019
Document de référence : [https://arxiv.org/abs/2003.07333](https://arxiv.org/abs/2003.07333)

---

## Installation

---

Avant de cloner ou de travailler sur le projet, installez Git LFS :

```bash
git lfs install
git clone https://github.com/Rayanekachbi/Demonstrateur-pour-la-RSVQA
cd Demonstrateur-pour-la-RSVQA
```

---

## Installation de Python

Si Python n’est pas installé sur votre machine :

1. Rendez-vous sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Téléchargez la dernière version stable.
3. Pendant l’installation, cochez la case `Add Python to PATH`.

Si `pip` n’est pas disponible, utilisez :

```bash
python -m ensurepip --upgrade
```

---


## Configuration du Backend (API)

1. Ouvrez un terminal dans le dossier du projet.
2. Accédez au dossier `backend` :

```bash
cd backend
```

3. Créez un environnement virtuel et activez-le :

```bash
py -3 -m venv .venv
.venv\Scripts\activate
```

## Téléchargement des fichiers lourds

Certains fichiers nécessaires (modèle et datasets) dépassent la limite autorisée par GitHub (100 Mo) et sont donc stockés en dehors du dépôt.

```bash
pip install gdown
python download_assets.py
```

4. Installez les dépendances :

```bash
pip install flask pillow flask-cors torch numpy torchvision transformers scikit-image
```

5. Lancez l’API :

```bash
python api.py
```

---

## Configuration du Frontend (Interface React)

1. Ouvrez un **nouveau terminal** dans le répertoire du projet.
2. Accédez au dossier `frontend` :

```bash
cd frontend
```

3. Installez les dépendances Node.js :

```bash
npm install
npm install react-router-dom
```

4. Lancez l’interface utilisateur :

```bash
npm start
```

---

## Relancer le projet après fermeture

### Terminal 1 – API :

```bash
cd backend
.venv\Scripts\activate
python api.py
```

### Terminal 2 – Interface :

```bash
cd frontend
npm start
```

---

## Résultat

Le démonstrateur RSVQA est désormais opérationnel.

---

---

# RSVQA Demonstrator – L2V Project

**Supervisor:** Boussaid Hichem
**Category:** Scientific Application
**Technologies:** Python,Flask, PyTorch, NumPy
**Keywords:** RSVQA, NLP, Deep Learning, Remote Sensing

---

## Context

**Remote Sensing Visual Question Answering (RSVQA)** is a research field at the crossroads of **remote sensing** and **artificial intelligence**. The goal is to enable a model to answer **natural language questions** about **satellite or aerial images**.

Questions may involve:

* object detection,
* quantity estimation,
* land type identification,
* spatial relationships, and more.

This demonstrator provides a **graphical interface** to apply an RSVQA model to one or more public datasets.

---

## Project Features

### 1. Dataset Selection

* Dropdown list to select a predefined dataset.
* Display of metadata: data type, number of images, etc.

### 2. Image Loading

* Loads a list of images specific to the selected dataset.
* Allows image selection and display.

### 3. Question Selection or Creation

* Choose an **existing question** linked to the image.
* Option to **enter a custom question** via text input.

### 4. Answer Generation

* Uses the VQA and ViLT models to generate answers.

---

## References

Lobry, S., Murray, J., Marcos, D., & Tuia, D. (2019).
*Visual Question Answering From Remote Sensing Images*. IGARSS 2019
Reference paper: [https://arxiv.org/abs/2003.07333](https://arxiv.org/abs/2003.07333)

---

## Installation

---

###  What to do

Before cloning or working with the repository, install Git LFS:

```bash
git lfs install
git clone https://github.com/Rayanekachbi/Demonstrateur-pour-la-RSVQA
cd Demonstrateur-pour-la-RSVQA
```

---

## Python Installation

If Python is not already installed:

1. Visit: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the **latest stable version**.
3. During installation, make sure to check the box `Add Python to PATH`.

If `pip` is missing, run:

```bash
python -m ensurepip --upgrade
```

---

## Backend Setup (API)

1. Open a terminal in the project root folder.
2. Navigate to the `backend` folder:

```bash
cd backend
```

3. Create and activate a virtual environment:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
```

## Downloading Large Files

Some required files (model and datasets) exceed GitHub's file size limit (100 MB) and are therefore stored externally.


```bash
pip install gdown
python download_assets.py
```

4. Install required dependencies:

```bash
pip install flask pillow flask-cors torch numpy torchvision transformers scikit-image
```

5. Start the API:

```bash
python api.py
```

---

## Frontend Setup (React Interface)

1. Open a **new terminal** in the project directory.
2. Navigate to the `frontend` folder:

```bash
cd frontend
```

3. Install the required Node.js modules:

```bash
npm install
npm install react-router-dom
```

4. Start the frontend:

```bash
npm start
```

---

## Restarting the Project

### Terminal 1 – Launch the API:

```bash
cd backend
.venv\Scripts\activate
python api.py
```

### Terminal 2 – Launch the Interface:

```bash
cd frontend
npm start
```

---

## Result

The RSVQA demonstrator is now up and running.

---

