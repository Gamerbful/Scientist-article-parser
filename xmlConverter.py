from lxml import etree
import xml.etree.cElementTree as ET

article = etree.Element("article")
preamble = etree.SubElement(article,"preamble")
preamble.text = "# mettre le fichier"
titre = etree.SubElement(article,"titre")
titre.text = "#mettre le titre" 
auteur = etree.SubElement(article,"auteur")
auteur.text = "#mettre les auteurs"
abstract = etree.SubElement(article,"abstract")
abstract.text = "#mettre l'abstract"
biblio = etree.SubElement(article,"biblio")
biblio.text = "#mettre la biblio"

tree = ET.ElementTree(article)
tree.write("filename.xml")


        