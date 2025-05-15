# libraries to be cleaned
import warnings

warnings.filterwarnings("ignore")
import os.path
import random
import skimage
import torch
import torchvision
import csv
from skimage import io
from torch.utils.data import Dataset
import torchvision.transforms as T
import torch.nn as nn
from torch.autograd import Variable
from torchvision import models as torchmodels
import numpy as np
import torchvision.transforms as transforms
from torch.utils.data import Dataset
from torchvision.models import ResNet50_Weights, ResNet152_Weights


# Sar
# from read_s1 import* #you modify import osgeo.gdal as gdal, cause errorsin pip install gdal
# from geography import *
#from sar_display import *

from transformers import BertTokenizer, VisualBertModel, VisualBertConfig, VisualBertForQuestionAnswering
from transformers import DistilBertModel, DistilBertConfig
from transformers import DistilBertTokenizer
from transformers import  DistilBertModel
# Disabilita gli avvisi temporaneamente
import torch.nn.functional as F
from scipy import interpolate

import json

MAX_ANSWERS = 5000 
LEN_QUESTION = 36


class VQAModel(nn.Module):
    def __init__(self, input_size=512, glimpses=1, pretrained=False,
                 device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')):  # vocab_answers, glimpses=2
        super(VQAModel, self).__init__()
        model_path = "distilbert-base-uncased"
        config = DistilBertConfig.from_pretrained(model_path)
        self.seq2vec = DistilBertModel.from_pretrained(model_path, config=config)
        for param in self.seq2vec.parameters():  # for param in self.seq2vec.embeddings.parameters():
            param.requires_grad = True

        # BDORTHO
        self.visualORTHO = torchmodels.resnet152(pretrained=True)

        for param in self.visualORTHO.parameters():
            param.requires_grad = False
        self.visualORTHO = torch.nn.Sequential(*list(self.visualORTHO.children())[:-1])
        self.classif1 = nn.Linear(1200, 256)
        self.classif2 = nn.Linear(256, 95)
        self.activation = nn.ReLU()
        self.drop = nn.Dropout(0.5)
        self.drop2 = nn.Dropout(0.5)
        self.linear_layerV = nn.Linear(2048, 1200)
        self.linear_layerT = nn.Linear(768, 1200)


    def _questionPart(self, input_q):
        q = self.seq2vec(**input_q)
        attention_mask = input_q['attention_mask']
        expanded_attention_mask = attention_mask.unsqueeze(2).expand(-1, -1, q[0].size(dim=2))  # 768 why 768?
        q = torch.sum(q[0] * expanded_attention_mask.float(), dim=1) / torch.sum(expanded_attention_mask,
                                                                                 dim=1)  # weighted
        x_q = nn.Tanh()(q)
        return x_q

    def forward(self, imageOrtho, question):
        question_feat = self._questionPart(question)
        ortho_feat = self.visualORTHO(imageOrtho)

        v_ortho = ortho_feat / (ortho_feat.norm(p=2, dim=1, keepdim=True).expand_as(ortho_feat) + 1e-8)
        visual_embeds = v_ortho.view(-1, 2048)

        x_v = self.drop(visual_embeds)
        x_v = self.linear_layerV(x_v)
        x_v = nn.Tanh()(x_v)
        x_q = self.drop(question_feat)
        x_q = self.linear_layerT(x_q)
        x_q = nn.Tanh()(x_q)
        x = torch.mul(x_v, x_q)
        x = nn.Tanh()(x)
        x = self.drop(x)
        x = self.classif1(x)
        x = nn.Tanh()(x)
        x = self.drop(x)
        x = self.classif2(x)

        return x
class VocabEncoder():
    def __init__(self, JSONFile, string=None, questions=True, range_numbers=False):
        self.encoder_type = 'answer'
        if questions:
            self.encoder_type = 'question'
        self.questions = questions
        self.range_numbers = range_numbers

        words = {}

        if JSONFile != None:
            with open(JSONFile) as json_data:
                self.data = json.load(json_data)[self.encoder_type + 's']
        else:
            if questions:
                self.data = [{'question': string}]
            else:
                self.data = [{'answer': string}]
        "2032".isnumeric()
        for i in range(len(self.data)):
            if self.data[i]["active"]:
                sentence = self.data[i][self.encoder_type]
                if sentence[-1] == "?" or sentence[-1] == ".":
                    sentence = sentence[:-1]
                if isinstance(sentence, list):
                    sentence = sentence[0]
                tokens = sentence.split()
                if not questions:
                    tokens = [sentence]
                for token in tokens:
                    token = token.lower()
                    if token[-2:] == 'm2' and not self.questions:
                        num = int(token[:-2])
                        if num > 0 and num <= 10:
                            token = "between 0m2 and 10m2"
                        if num > 10 and num <= 100:
                            token = "between 10m2 and 100m2"
                        if num > 100 and num <= 1000:
                            token = "between 100m2 and 1000m2"
                        if num > 1000:
                            token = "more than 1000m2"
                    elif token[-1:] == "m":
                        try:
                            token = str(round(float(token[:-1]))) + "m"
                        except ValueError:
                            pass
                    if token not in words:
                        words[token] = 1
                    else:
                        words[token] += 1

        sorted_words = sorted(words.items(), key=lambda kv: kv[1], reverse=True)
        print(len(sorted_words))
        self.words = {'<EOS>': 0}
        self.list_words = ['<EOS>']
        for i, word in enumerate(sorted_words):
            if self.encoder_type == 'answer':
                if i >= MAX_ANSWERS:
                    print("MAX_ANSWERS")
                    break
            self.words[word[0]] = i + 1
            self.list_words.append(word[0])

    def encode(self, sentence):
        res = []
        if sentence[-1] == "?" or sentence[-1] == ".":
            sentence = sentence[:-1]
        if isinstance(sentence, list):
            sentence = sentence[0]
        tokens = sentence.split()
        if not self.questions:
            tokens = [sentence]
        for token in tokens:
            token = token.lower()
            if token[-2:] == 'm2' and not self.questions:
                num = int(token[:-2])
                if num > 0 and num <= 10:
                    token = "between 0m2 and 10m2"
                if num > 10 and num <= 100:
                    token = "between 10m2 and 100m2"
                if num > 100 and num <= 1000:
                    token = "between 100m2 and 1000m2"
                if num > 1000:
                    token = "more than 1000m2"
            elif token[-1:] == "m" and not self.questions:
                try:
                    token = str(round(float(token[:-1]))) + "m"
                except ValueError:
                    pass
            res.append(self.words[token])

        if self.questions:
            res.append(self.words['<EOS>'])

        while self.questions and len(res) < LEN_QUESTION:
            res.append(self.words['<EOS>'])
        res = res[:LEN_QUESTION]
        return res

    def getVocab(self):
        return self.list_words


    def decode(self, sentence):
        res = ""
        for i in sentence:
            if i == 0:
                break
            res += self.list_words[i]
            res += " "
        res = res[:-1]
        if self.questions:
            res += "?"
        return res


"""if __name__ == "__main__":
    #Definir le model
    model = VQAModel()
    encoder_answers = VocabEncoder("HR-RSVQA/data/USGSanswers.json", questions=False)
    model_name = "BigModel_30.tar"
    checkpoint = torch.load(model_name,torch.device('cpu'))

    #Charger les poids du model
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint["optimizer"])
    #Definir le tokenizer (ne rien changer de cette ligne)
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    #Remplacer question_str par la question
    question_str = "What is the capital of France?"
    question = tokenizer(question_str, return_tensors="pt", padding='max_length', max_length=36,
              add_special_tokens=True)
    #Lire l'image
    img = Image.open('HR-RSVQA/data/France.jpg') #CECI EST UN EXEMPLE SEULEMENT
    img = torch.from_numpy(img).unsqueeze(0)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    model = model.to(device)
    model.eval()

    question = question.to(device)
    img = img.float().to(device)

    # Run the model and compute the loss
    pred = torch.max((model(img,question).data), dim=1)
    #Reponse du modèle:
    answer = encoder_answers.decode(pred[indices])"""