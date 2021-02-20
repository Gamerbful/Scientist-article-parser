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
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

ps = PorterStemmer()
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

        ['Juan-Manuel Torres-Moreno', 'author'],
        ['Florian Boudin ♮ and Marc El-B`eze', 'author'],
        ['Juan-Manuel Torres-Moreno', 'author'],
        ['Juan-Manuel Torres-Moreno', 'author'],
        ['Introduction', 'introduction'],
        ['Extensive experiments on query-oriented multi-', 'introduction'],
        ['document summarization have been carried out', 'introduction'],
        ['over the past few years.', 'introduction'],
        ['Most of the strategies', 'introduction'],
        ['to produce summaries are based on an extrac-', 'introduction'],
        ['tion method, which identifies salient textual seg-', 'introduction'],
        ['ments, most often sentences, in documents. Sen-', 'introduction'],
        ['tences containing the most salient concepts are se-', 'introduction'],
        ['lected, ordered and assembled according to their', 'introduction'],
        ['relevance to produce summaries (also called ex-', 'introduction'],
        ['tracts) (Mani and Maybury, 1999).', 'introduction'],
        ['Recently emerged from the Document Under-', 'introduction'],
        ['standing Conference (DUC) 20071, update sum-', 'introduction'],
        ['marization attempts to enhance summarization', 'introduction'],
        ['when more information about knowledge acquired', 'introduction'],
        ['by the user is available. It asks the following ques-', 'introduction'],
        ['tion: has the user already read documents on the', 'introduction'],
        ['topic? In the case of a positive answer, producing', 'introduction'],
        ['an extract focusing on only new facts is of inter-', 'introduction'],
        ['est. In this way, an important issue is introduced:', 'introduction']]

for row in rows:
    word_list = word_tokenize(row[0])
    word_list = [word for word in word_list if not word in stopwords.words()]
    for word in word_list:
        word = ps.stem(word)
    row[0] = ' '.join(word_list)

print(rows)
training_data = pd.DataFrame(rows, columns=columns)


def vectorizer( feature ):

    stmt_docs = [row['sent'] for index,row in training_data.iterrows() if row['class'] == feature ]
    vec_s = CountVectorizer()
    X_s = vec_s.fit_transform(stmt_docs)
    tdm_s = pd.DataFrame(X_s.toarray(), columns=vec_s.get_feature_names())
    return vec_s,X_s;

vec_q, X_q = vectorizer('titre')
vec_i, X_i = vectorizer('introduction')
vec_a, X_a = vectorizer('author')
def toDico ( vec, X ):

    word_list = vec.get_feature_names()
    count_list = X.toarray().sum(axis=0)
    return  count_list, dict(zip(word_list,count_list))

count_list_q, freq_q = toDico(vec_q, X_q)
count_list_i, freq_i = toDico(vec_i, X_i)
count_list_a, freq_a = toDico(vec_a, X_a)

docs = [row['sent'] for index,row in training_data.iterrows()]

vec = CountVectorizer()
X = vec.fit_transform(docs)

total_features = len(vec.get_feature_names())

total_cnts_features_q = count_list_q.sum(axis=0)
total_cnts_features_i = count_list_i.sum(axis=0)
total_cnts_features_a = count_list_a.sum(axis=0)

new_sentence = input(str("yo met une phrase : "))
new_word_list = word_tokenize(new_sentence)
new_word_list = [word for word in new_word_list if not word in stopwords.words()]
for word in new_word_list:
    word = ps.stem(word)


def probabilist(total_cnts_features,freq):

    prob_s_with_ls = []
    for word in new_word_list:
        if word in freq.keys():
            count = freq[word]
        else:
            count = 0
        prob_s_with_ls.append((count + 1)/(total_cnts_features + total_features))
    bobo = dict(zip(new_word_list,prob_s_with_ls))
    bobo_res = 1
    for word in new_word_list:
        bobo_res = bobo_res*bobo[word]
    return bobo_res* ( total_cnts_features/total_features)


probas = dict();
probas["author"] = probabilist(total_cnts_features_a, freq_a)
probas["intro"] = probabilist(total_cnts_features_i, freq_i)
probas["titre"] = probabilist(total_cnts_features_q, freq_q)

print(probas)

print(max(probas, key=probas.get))
