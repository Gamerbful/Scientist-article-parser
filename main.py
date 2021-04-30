import fitz  # this is pymupdf

import nltk
from nltk.tag import StanfordNERTagger
from nltk.stem import PorterStemmer

from lxml import etree
import xml.etree.cElementTree as ET

import os, sys, re

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

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
introPattern = "(^.*[Ii][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn].*$)"
introMatcher = re.compile(introPattern)
concPattern = "^.*[C][Oo][Nn][Cc][Ll][Uu][Ss][Ii][Oo][Nn].*$"
concMatcher = re.compile(concPattern)
referencesPattern = ".*(References|REFERENCES)"
referencesMatcher = re.compile(referencesPattern)
emailPattern = "(^.*@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
emailMatcher = re.compile(emailPattern)
discussionPattern = "^.*[D][Ii][Ss][Cc][Uu][Ss][Ss][Ii][Oo][Nn].*$"
discussionMatcher = re.compile(discussionPattern)
acknowlegmentsPattern = "^.*[Aa][Cc][Kk][Nn][Oo][Ww][Ll][Ee][Dd][Gg]([Ee])?[Mm][Ee][Nn][Tt][Ss].*$"
acknowlegmentsMatcher = re.compile(acknowlegmentsPattern)
endIntroductionPattern = "((\s)*(2|II)(\.)?\s[A-Z](\w|\s|,)*$)|(^2(\s)?$)|(^2.(\s)*$)"
endIntroductionMatcher = re.compile(endIntroductionPattern)

# --- Function for name recognition ---
def find_author(text):
    res = ""
    name = ""
    found = 0
    i = 0
    max = 10
    splitedText = text.splitlines()
    while i<max:

        words = nltk.word_tokenize(splitedText[i])
        for elt in ner_tagger.tag(words):
            if elt[1] == "PERSON":
                name += elt[0] + " "
                found += 1
            else:
                if name != "" and found > 1:
                    res += name + ", "
                    name = ""
                    found = 0
        if name != "":
            if found > 1:
                res += name + ", "
                name = ""
                max = max + 2
        found = 0
        i = i +1
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

def find_abstract(text, ACTUAL_LINE):
    res = ""
    vf = True
    splitedText = text.splitlines()
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if vf and abstractMatcher.match(line):
                vf = False
            if (not vf) and (not introMatcher.match(line)):
                res = res + line
            if (not vf) and introMatcher.match(line):
                ACTUAL_LINE = CPT
                break
    if vf:
        return ["No abstract was found",-1]
    return [res, ACTUAL_LINE]

def find_references(text, ACTUAL_LINE):
    res = ""
    splitedText = text.splitlines()
    vf = False
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if referencesMatcher.match(line):
                vf = True
            if vf:
                res = res + line
    if not vf:
        return ["No references was found",-1]
    return [res, 0]

def find_discussion(text, ACTUAL_LINE):
    res = ""
    vf = False
    splitedText = text.splitlines()
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if vf:
                if acknowlegmentsMatcher.match(line) or concMatcher.match(line):
                    ACTUAL_LINE = CPT
                    break
                else:
                    res = res + line
            if not vf and discussionMatcher.match(line):
                vf = True
    if not vf:
        return ["No discussion was found",-1]
    return [res, ACTUAL_LINE];


def find_conclusion(text, ACTUAL_LINE):
    res=""
    splitedText = text.splitlines()
    vf = True
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if vf and concMatcher.match(line):
                vf = False
            if (not vf) and (not referencesMatcher.match(line) and not acknowlegmentsMatcher.match(line)):
                res = res + line
            if (not vf) and ( referencesMatcher.match(line) or acknowlegmentsMatcher.match(line)):
                ACTUAL_LINE = CPT
                break
    if vf:
        return ["No conclusion was found",-1]
    return [res,ACTUAL_LINE];

def find_introduction(text,ACTUAL_LINE):
    res = ""
    splitedText = text.splitlines()
    vf = False
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if vf:
                if endIntroductionMatcher.match(line):
                    ACTUAL_LINE = CPT
                    break
                else:
                    res = res + line
            if not vf and introMatcher.match(line):
                vf = True
    if not vf:
        return ["No introduction was found",-1]
    return [res,ACTUAL_LINE];

def find_corp(text,ACTUAL_LINE):
    res = ""
    splitedText = text.splitlines()
    vf = False
    CPT = 0
    for line in splitedText:
        CPT += 1
        if CPT >= ACTUAL_LINE:
            if vf:
                if concMatcher.match(line) or discussionMatcher.match(line):
                    ACTUAL_LINE = CPT
                    break
                else:
                    res = res + line
            if not vf and endIntroductionMatcher.match(line):
                vf = True
    if not vf:
        return ["No corp was found",-1]
    return [res,ACTUAL_LINE];

def find_affiliation(text,author):
    res=""
    authors = author.split(", ")
    affil= []
    emails = []
    splitedText = text.splitlines()
    trouve = False
    for line in splitedText:
        if not trouve:
            for author in authors:
                words = author.split(" ")
                for word in words:
                    if word in line.split(" "):
                        trouve = True
                        break
        else:
            if emailMatcher.match(line):
                affil.insert(len(affil),res)
                emails.insert(len(emails),line)
                res = ""
            else:
                res = res +line
        if abstractMatcher.match(line):
            break

    return (affil,emails);

def write_xml(text,name):
    ACTUAL_LINE = 0

    author = find_author(text)
    title = find_title(text, author)
    affilia = find_affiliation(text,author)
    affil = affilia[0]
    emails = affilia[1]

    author = find_author(text)
    title = find_title(text, author)
    abstract = find_abstract(text,ACTUAL_LINE)
    if abstract[1] >= 0:
        ACTUAL_LINE = abstract[1] - 2
    introduction = find_introduction(text,ACTUAL_LINE)
    if introduction[1] >= 0:
        ACTUAL_LINE = introduction[1] - 2
    corp = find_corp(text,ACTUAL_LINE)
    if corp[1] >= 0:
        ACTUAL_LINE = corp[1] - 2
    discussion = find_discussion(text,ACTUAL_LINE)
    if discussion[1] >= 0:
        ACTUAL_LINE = discussion[1] - 2
    conclu = find_conclusion(text,ACTUAL_LINE)
    if conclu[1] >= 0:
        ACTUAL_LINE = conclu[1] - 2
    references = find_references(text,ACTUAL_LINE)

    article = etree.Element("article")
    preamble = etree.SubElement(article,"preamble")
    preamble.text = name + ".pdf"
    titre = etree.SubElement(article,"titre")
    titre.text = title
    auteurs = etree.SubElement(article,"auteurs")
    for aut in author.split(", "):
        auteur = etree.SubElement(auteurs,"auteur")
        auteur.text = aut
        if len(emails) > 1:
            auteur.text = auteur.text + " " + emails[0]
            emails.pop(0)
        if len(emails) == 1:
            auteur.text = auteur.text + " " + emails[0]

        affiliation = etree.SubElement(auteurs,"affiliation")
        if len(affil) > 1:
            affiliation.text = affil[0]
            affil.pop(0)
        elif len(affil) == 0:
            affiliation.text = "No affiliation"
        elif len(affil) == 1:
            affiliation.text = affil[0]

    abstractB = etree.SubElement(article,"abstract")
    abstractB.text = abstract[0]
    introductionB = etree.SubElement(article,"introduction")
    introductionB.text = introduction[0]
    corpB = etree.SubElement(article,"corp")
    corpB.text = corp[0]
    discussionB = etree.SubElement(article,"discussion")
    discussionB.text = discussion[0]
    conclusion = etree.SubElement(article,"conclusion")
    conclusion.text = conclu[0]
    biblio = etree.SubElement(article,"biblio")
    biblio.text = references[0]

    file = open("res/" + name + ".xml","w+", encoding='utf-8')
    file.write((etree.tostring(article,pretty_print=True).decode("utf-8")))
    file.close()

def write_text(text,name):
    ACTUAL_LINE = 0
    author = find_author(text)
    title = find_title(text, author)
    abstract = find_abstract(text,ACTUAL_LINE)
    if abstract[1] >= 0:
        ACTUAL_LINE = abstract[1] - 2
    introduction = find_introduction(text,ACTUAL_LINE)
    if introduction[1] >= 0:
        ACTUAL_LINE = introduction[1] - 2
    corp = find_corp(text,ACTUAL_LINE)
    if corp[1] >= 0:
        ACTUAL_LINE = corp[1] - 2
    discussion = find_discussion(text,ACTUAL_LINE)
    if discussion[1] >= 0:
        ACTUAL_LINE = discussion[1] - 2
    conclu = find_conclusion(text,ACTUAL_LINE)
    if conclu[1] >= 0:
        ACTUAL_LINE = conclu[1] - 2
    references = find_references(text,ACTUAL_LINE)

    file = open("res/" + name + ".txt","w+", encoding='utf-8')
    file.write("Nom du fichier: " + f + "\n\n")
    file.write("Titre: " + title + "\n\n")
    file.write("Auteurs: " + author + "\n\n")
    file.write(abstract[0].replace("Abstract","Abstract : ") + "\n\n")
    file.write("Introduction : "+introduction[0]+"\n\n")
    file.write("Corp : "+corp[0]+"\n\n")
    file.write("Discussion : "+discussion[0]+"\n\n")
    file.write("Conclusion : "+conclu[0]+"\n\n")
    file.write(references[0].replace("References","References : ") + "\n\n")
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

    #if len(dirl) > 0:
    if dirname[len(dirname)-1] != '/':
        dirname += '/'
    try:
        os.mkdir("./res")
    except FileExistsError:
        pass

    dirl = []

    try:
        dirl = os.listdir(dirname)
        root = tk.Tk()
        root.withdraw()
        MsgBox = tk.messagebox.askquestion('','Select only specific files ?')
        if MsgBox == 'yes':
            dirl = filedialog.askopenfilenames(parent=root,title='Choose files', filetypes=[('PDF file','*.pdf')], initialdir=dirname)
            dirl = list(dirl)
            for index, file in enumerate(dirl):
                f = file.split('/')
                dirl[index] = f[len(f)-1]
            root.quit()

        print("Running ...")
    except FileNotFoundError:
        print("Directory does not exist")
    except NotADirectoryError:
        print("Not a directory")

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
