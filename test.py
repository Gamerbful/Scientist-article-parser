import fitz  # this is pymupdf

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

for i in range(0,len(list)):
    file = open("res/file"+str(i), "w+", encoding='utf-8')
    with fitz.open(s_path+list[i]) as doc:
        text = ""
        for page in doc:
            text += page.getText()
        print(text)
        file.write(text)
        file.close()
