import fitz  # this is pymupdf

import nltk
from nltk.tag import StanfordNERTagger
from nltk.stem import PorterStemmer

from lxml import etree
import xml.etree.cElementTree as ET

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
concPattern = "^.*[C][Oo][Nn][Cc][Ll][Uu][Ss][Ii][Oo][Nn].*$"
concMatcher = re.compile(concPattern)
referencesPattern = "References"
referencesMatcher = re.compile(referencesPattern)
emailPattern = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
emailMatcher = re.compile(emailPattern)

discussionPattern = "^.*[D][Ii][Ss][Cc][Uu][Ss][Ss][Ii][Oo][Nn].*$"
discussionMatcher = re.compile(discussionPattern)

acknowlegmentsPattern = "^.*[Aa][Cc][Kk][Nn][Oo][Ww][Ll][Ee][Dd][Gg][Mm][Ee][Nn][Tt][Ss].*$"
acknowlegmentsMatcher = re.compile(acknowlegmentsPattern)

conclusionsPattern = "^.*[Cc][Oo][Nn][Cc][Ll][Uu][Ss][Ii][Oo][Nn][Ss].*$"
conclusionsMatcher = re.compile(conclusionsPattern)

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
                    res += name + ", "
                    name = ""
                    found = 0
        if name != "":
            if found > 1:
                res += name + ", "
                name = ""
        found = 0
    return res[0:len(res)-3]

def find_title(text,author):
    res = ""
    splitedText = text.splitlines()
    authorList = author.split(" , ")
    for i in range(0,5):
        if not(numberMatcher.match(splitedText[i])):
            if authorList[0] in splitedText[i]:
                break
            res += splitedText[i] + " "
    return res

def find_email(text):
    res = ""
    splitedText = text.splitlines()

    for i in range(0,10):
        words = splitedText[i].split(" ")
        for word in words:
            if emailMatcher.match(word):
                res += " , " + splitedText[i] + " "
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
        res = "No abstract was found"
    return res

def find_references(text):
    res = ""
    splitedText = text.splitlines()
    vf = False
    for line in splitedText:
        if referencesMatcher.match(line):
            vf = True
        if vf:
            res = res + line
    if not vf:
        res = "No references was found"
    return res

def find_discussion(text):
    res = ""
    vf = False
    splitedText = text.splitlines()
    for line in splitedText:
        if vf:
            if acknowlegmentsMatcher.match(line) or conclusionsMatcher.match(line):
                break
            else:
                res = res + line
        if not vf and discussionMatcher.match(line):
            vf = True
    if not vf:
        res = "No discussion was found"
    return res;


def find_conclusion(text):
    res=""
    splitedText = text.splitlines()
    vf = True
    for line in splitedText:
        if vf and concMatcher.match(line):
            vf = False
        if (not vf) and (not referencesMatcher.match(line)):
            res = res + line
        if (not vf) and referencesMatcher.match(line):
            break
    if vf:
        res = "No conclusion was found"
    return res;


def write_xml(text,name):
    author = find_author(text)
    title = find_title(text, author)
    abstract = find_abstract(text)
    refs = find_references(text)
    conclu = find_conclusion(text)

    article = etree.Element("article")
    preamble = etree.SubElement(article,"preamble")
    preamble.text = name + ".pdf"
    titre = etree.SubElement(article,"titre")
    titre.text = title
    auteur = etree.SubElement(article,"auteur")
    auteur.text = author
    abstractB = etree.SubElement(article,"abstract")
    abstractB.text = abstract
    biblio = etree.SubElement(article,"biblio")
    biblio.text = refs
    conclusion = etree.SubElement(article,"conclusion")
    conclusion.text = conclu
    
    file = open("res/" + name + ".xml","w+", encoding='utf-8')
    file.write((etree.tostring(article,pretty_print=True).decode("utf-8")))
    file.close()

def write_text(text,name):
    author = find_author(text)
    title = find_title(text, author)
    abstract = find_abstract(text)
    references = find_references(text)
    discussion = find_discussion(text)

    file = open("res/" + name + ".txt","w+", encoding='utf-8')
    file.write("Nom du fichier: " + f + "\n\n")
    file.write("Titre: " + title + "\n\n")
    file.write("Auteurs: " + author + "\n\n")
    file.write(abstract.replace("Abstract","Abstract : ") + "\n\n")
    file.write(references.replace("References","References : ") + "\n\n")
    file.write("Discussion : "+discussion+"\n\n")
    file.close()

if __name__ == '__main__':

    if len(sys.argv) > 3:
        print("usage: main.py [-x|-t] directory")
        sys.exit(1)

    dirname = ""
    command = ""

    if len(sys.argv) < 3:
        dirname = sys.argv[1]
    else:
        if sys.argv[1] == "-x" or sys.argv[1] == "-t":
            dirname = sys.argv[2]
            command = sys.argv[1]
        elif sys.argv[2] == "-x" or sys.argv[2] == "-t":
            dirname = sys.argv[1]
            command = sys.argv[2]
        else:
            print("usage: main.py directory [-x|-t]")
            sys.exit(1)

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

    print("Running ...")

    for f in dirl:
        print("Parse of : "+f)
        try:
            with fitz.open(dirname + f) as doc:
                text = ""
                for page in doc:
                    text += page.get_text().replace("^i","î").replace("`e","e").replace("´e","e")
                if command != "":
                    if command == "-x":
                        write_xml(text,f[:len(f)-4])
                    elif command == "-t":
                        write_text(text,f[:len(f)-4])
                    else:
                        print("usage: main.py directory [-x|-t]")
                        sys.exit(1)
                else:
                    write_text(text,f[:len(f)-4])
        except RuntimeError:
            print("Cannot open file \"" + f + "\" (not PDF or may be corrupted)")
