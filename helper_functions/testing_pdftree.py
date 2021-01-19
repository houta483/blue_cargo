# import pdftotree
import pdfminer

# with open('./test.html', 'a+') as file:
#     file.write(pdftotree.parse(
#         "/Users/Tanner/code/products/glucose/original_data/CarliWilliams_01-15-2021.pdf", html_path=None, model_type=None, model_path=None, visualize=True))

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

output_string = StringIO()
with open("/Users/Tanner/code/products/glucose/original_data/CarliWilliams_01-15-2021.pdf", 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

print(output_string.getvalue())
