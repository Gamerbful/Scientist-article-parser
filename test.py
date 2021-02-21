import fitz  # this is pymupdf
import fitz  # this is pymupdf

import os, sys, re
from nltk.stem import PorterStemmer
import nltk
from nltk.tag import StanfordNERTagger

jar = './stanford-ner-2020-11-17/stanford-ner.jar'
model = './stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz'

# Prepare NER tagger with english model
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')



# Test push Kiki

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

    partPattern = "^[0-9](\.[0-9])*$"
    matcher = re.compile(partPattern)



    auteur = "autheurs : "
    index = 0
    nom = ""
    trouve = 0

    def name_recognition(words):
        global nom,index,auteur,trouve
        for elt in ner_tagger.tag(words):
            if elt[1] == "PERSON":
                nom += elt[0] + " "
                trouve += 1
            else:
                if nom != "":
                    auteur += nom + "et "
                    nom = ""
                    trouve = 0
    def check():
        global nom,auteur,trouve
        if nom != "":
            if trouve > 1:
                auteur += nom + "et "
                nom = ""

    for f in dirl:
        try:
            with fitz.open(dirname + f) as doc:
                text = ""
                index = 0
                auteur = ""
                trouve = 0
                for page in doc:
                    pageTxt = page.get_text().replace("`","").replace("´","").replace("^","")
                    for line in pageTxt.splitlines():
                        if index < 10:
                            words = nltk.word_tokenize(line)
                            name_recognition(words)
                            check()
                        if matcher.match(line):
                            text += '\nNEWGROUP\n' + line + '\n'
                        else:
                            text += line + '\n'
                        index += 1
                print( f+" : "+   auteur[0:len(auteur)-3])
                fichier = open("res/" + f[:len(f)-4] + ".txt","w+", encoding='utf-8')
                fichier.write("Nom du fichier: " + f + "\n\n")
                fichier.write(text)
                fichier.close()
        except RuntimeError:
            print("Cannot open file \"" + f + "\" (not PDF or may be corrupted)")
