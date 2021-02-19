import fitz  # this is pymupdf
import numpy as np, pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import CountVectorizer

import nltk
from nltk.tokenize import word_tokenize

sns.set() # use seaborn plotting style

s_path = 'articles/'
path1 = 'Boudin-Torres-2006.pdf'
path2 = 'Das_Martins.pdf'
path3 = 'Gonzalez_2018_Wisebe.pdf'
path4 = 'Iria_Juan-Manuel_Gerardo.pdf'
path5 = 'kessler94715.pdf'
path6 = 'kesslerMETICS-ICDIM2019.pdf'
path7 = 'mikheev J02-3002.pdf'
path8 = 'Mikolov.pdf'
path9 = 'Nasr.pdf'
path10 = 'Torres.pdf'
path11 = 'Torres-moreno1998.pdf'
path12 = 'jing-cutepaste.pdf'

list = (path1,path2,path3,path4,path5,path6,path7,path8,path9,path10,path11);

for i in range(0,len(list)):
    file = open("res/file"+str(i), "w+", encoding='utf-8')
    with fitz.open(s_path+list[i]) as doc:
        text = ""
        for page in doc:
            text += page.getText()
        file.write(text)
        file.close()




columns = ['sent', 'class']
rows = []

rows = [['A Scalable MMR Approach to Sentence Scoring for Multi-Document Update Summarization', 'titre'],
        ['A Survey on Automatic Text Summarization', 'titre'],
        ['WiSeBE: Window-Based Sentence Boundary Evaluation', 'titre'],
        ['On the Development of the RST Spanish Treebank', 'titre'],
        ['Extraction of terminology in the field of construction', 'titre'],
        ['An NLP Tool Suite for Processing Word Lattices','titre'],
        ["The increasing availability of online information has necessitated intensive", 'abstract'],
        ['Aresearch in the area of automatic text summarization within the Natural Lan-', 'abstract']]

training_data = pd.DataFrame(rows, columns=columns)

stmt_docs = [row['sent'] for index,row in training_data.iterrows() if row['class'] == 'abstract']

vec_s = CountVectorizer()
X_s = vec_s.fit_transform(stmt_docs)
tdm_s = pd.DataFrame(X_s.toarray(), columns=vec_s.get_feature_names())


q_docs = [row['sent'] for index,row in training_data.iterrows() if row['class'] == 'titre']

vec_q = CountVectorizer()
X_q = vec_q.fit_transform(q_docs)
tdm_q = pd.DataFrame(X_q.toarray(), columns=vec_q.get_feature_names())


word_list_s = vec_s.get_feature_names();
count_list_s = X_s.toarray().sum(axis=0)
freq_s = dict(zip(word_list_s,count_list_s))

word_list_q = vec_q.get_feature_names();
count_list_q = X_q.toarray().sum(axis=0)
freq_q = dict(zip(word_list_q,count_list_q))

docs = [row['sent'] for index,row in training_data.iterrows()]

vec = CountVectorizer()
X = vec.fit_transform(docs)

total_features = len(vec.get_feature_names())

total_cnts_features_s = count_list_s.sum(axis=0)
total_cnts_features_q = count_list_q.sum(axis=0)

new_sentence = input(str("yo met une phrase : "))
new_word_list = word_tokenize(new_sentence)


prob_s_with_ls = []
for word in new_word_list:
    if word in freq_s.keys():
        count = freq_s[word]
    else:
        count = 0
    prob_s_with_ls.append((count + 1)/(total_cnts_features_s + total_features))
bobo = dict(zip(new_word_list,prob_s_with_ls))
bobo_res = 1
for word in new_word_list:
    bobo_res = bobo_res*bobo[word]

prob_q_with_ls = []
for word in new_word_list:
    if word in freq_q.keys():
        count = freq_q[word]
    else:
        count = 0
    prob_q_with_ls.append((count + 1)/(total_cnts_features_q + total_features))
baba = dict(zip(new_word_list,prob_q_with_ls))
baba_res = 1
for word in new_word_list:
    baba_res = baba_res*baba[word]




if baba_res*(6/8) > bobo_res*(2/8):
    print( "c'est un titre!")
else:
    print( "c'est un abstract ")
