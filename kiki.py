import fitz  # this is pymupdf

# For name recognition
import nltk
nltk.download('words')
from nltk.tag.stanford import StanfordNERTagger

import os, sys, re



jar = './stanford-ner-2020-11-17/stanford-ner.jar'
model = './stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz'

# Prepare NER tagger with english model
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

# --- Function for name recognition ---
def extract_entities(line):
    for chunk in nltk.ne_chunk(ner_tagger.tag(nltk.word_tokenize(line))):
        if hasattr(chunk, 'label'):
            if chunk.label() == 'PERSON':
                print(' '.join(c[0] for c in chunk.leaves()))

# --- Main ---
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

    #partPattern = "^[0-9](\.[0-9])*$"
    #matcher = re.compile(partPattern)

    for f in dirl:
        #try:
        print(f)
        i = 0
        with fitz.open(dirname + f) as doc:
            text = ""
            for page in doc:
                pageTxt = page.getText().replace("`e","è").replace("´e","é")
                for line in pageTxt.splitlines():
                    if i < 10:
                        extract_entities(line)
                    #if matcher.match(line):
                        #text += '\nNEWGROUP\n' + line + '\n'
                    #else:
                    i = i + 1
                    text += line + '\n'
            fichier = open("res/" + f[:len(f)-4] + ".txt","w+", encoding='utf-8')
            fichier.write("Nom du fichier: " + f + "\n\n")
            fichier.write(text)
            fichier.close()
            print("\n\n")
        #except RuntimeError:
            #print("Cannot open file \"" + f + "\" (not PDF or may be corrupted)")
