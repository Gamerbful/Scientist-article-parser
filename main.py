import fitz  # this is pymupdf

import nltk
from nltk.tag import StanfordNERTagger
from nltk.stem import PorterStemmer

import os, sys, re

jar = './stanford-ner-2020-11-17/stanford-ner.jar'
model = './stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz'

# Prepare NER tagger with english model
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

partPattern = "^[0-9](\.[0-9])*$"
partMatcher = re.compile(partPattern)
numberPattern = "^.*[0-9].*$"
numberMatcher = re.compile(numberPattern)
abstractPattern = "^.*[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt].*$"
abstractMatcher = re.compile(abstractPattern)
introPattern = "^.*[Ii][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn].*$"
introMatcher = re.compile(introPattern)

# --- Function for name recognition ---
def find_author(text):
    res = ""
    name = ""
    found = 0
    splitedText = text.splitlines()
    for i in range(0,10):
        words = nltk.word_tokenize(splitedText[i])
        for elt in ner_tagger.tag(words):
            if elt[1] == "PERSON":
                name += elt[0] + " "
                found += 1
            else:
                if name != "":
                    res += name + "& "
                    name = ""
                    found = 0
        if name != "":
            if found > 1:
                res += name + "& "
                name = ""
        found = 0
    return res[0:len(res)-3]

def find_title(text,author):
    res = ""
    splitedText = text.splitlines()
    authorList = author.split(" & ")
    #print(authorList)
    for i in range(0,5):
        if not(numberMatcher.match(splitedText[i])):
            if authorList[0] in splitedText[i]:
                break
            res += splitedText[i] + " "
    return res

def find_abstract(text):
    res = ""
    vf = True
    splitedText = text.splitlines()
    for line in splitedText:
        if vf and abstractMatcher.match(line):
            vf = False
        if (not vf) and (not introMatcher.match(line)):
            res = res + line
        if (not vf) and introMatcher.match(line):
            break
    if vf:
        res = "Aucun abstract n'a été trouvé"
    return res

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("usage: parser.py directory")
        sys.exit(1)

    dirname = sys.argv[1]

    dirl = []
    try:
        dirl = os.listdir(dirname)
    except FileNotFoundError:
        print("Directory does not exist")
    except NotADirectoryError:
        print("Not a directory")

    if len(dirl) > 0:
        if dirname[len(dirname)-1] != '/':
            dirname += '/'
        try:
            os.mkdir("./res")
        except FileExistsError:
            pass

    for f in dirl:
        try:
            with fitz.open(dirname + f) as doc:
                text = ""
                for page in doc:
                    text += page.get_text().replace("^i","î").replace("`e","è").replace("´e","é")
                fichier = open("res/" + f[:len(f)-4] + ".txt","w+", encoding='utf-8')
                fichier.write("Nom du fichier: " + f + "\n\n")
                author = find_author(text)
                title = find_title(text, author)
                abstract = find_abstract(text)
                fichier.write("Titre: " + title + "\n\n")
                fichier.write("Auteurs: " + author + "\n\n")
                fichier.write(abstract.replace("Abstract","Abstract : ") + "\n\n")
                # fichier.write(text)
                fichier.close()
        except RuntimeError:
            print("Cannot open file \"" + f + "\" (not PDF or may be corrupted)")
