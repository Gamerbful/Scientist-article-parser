# get_doc_info.py

from PyPDF2 import PdfFileReader
from os import listdir
from os.path import isfile, join
import glob

def get_info(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    print(path)
    title = info.title
    print("Voici le titre :"+title)
    author = info.author
    print("Voici l'auteur :"+author)



if __name__ == '__main__':
    for file in glob.glob("articles/*.pdf"):
        print("\n")
        get_info(file)
