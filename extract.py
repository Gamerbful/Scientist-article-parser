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
    try:
        print("Voici le titre :"+str(title))
    author = info.author
        print("Voici le auteur :"+str(author))


if __name__ == '__main__':
    for file in glob.glob("articles/*.pdf"):
        print("\n")
        get_info(file)
