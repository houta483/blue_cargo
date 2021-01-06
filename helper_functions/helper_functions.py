import fitz
import os
from PIL import Image
from string import ascii_lowercase
from PyPDF2 import PdfFileReader, PdfFileWriter
import pytesseract
import tabula
import pdfplumber
from tabula import read_pdf
import csv
import pandas as pd
import re


def find_correct_pages(metric, pdf):
    print('find_corect_pages')
    pages = []
    for index, page in enumerate(pdf):
        if metric in page:
            pages.append(index)
    return pages


def write_data_to_txt_file(pages, writable_pdf, where_to_save_pdf, person):
    print('write_data_to_txt_file')
    pdfWriter = PdfFileWriter()

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    with open(f"{where_to_save_pdf}/truncated_data_{person}", 'wb') as f:
        pdfWriter.write(f)
        f.close()

    for index, files in enumerate(os.listdir('./truncated_data')):
        file_path_to_scrape = os.path.join('./truncated_data', files)
        with pdfplumber.open(file_path_to_scrape) as pdf:
            for x in range(len(pages)):
                page = pdf.pages[x]
                text = page.extract_text(x_tolerance=3, y_tolerance=3)

                with open('extracted_data/extracted_data.txt', "a") as f:
                    f.write(text)


def filter_txt_data(person):
    print('filter_txt_data')
    with open('extracted_data/extracted_data.txt', 'r') as f:
        lines = f.readlines()

        for index, line in enumerate(lines):
            if any(x in line for x in ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')):
                with open('extracted_data/filtered_text_data.txt', "a") as f:
                    line = line.replace('180', '')
                    line = line.replace('  ', ' ')
                    line = person + " " + line
                    line = line.replace('_', '')
                    pattern = re.compile(r'\d{1,}-\d{1,}-\d{1,}.pdf ')
                    line = re.sub(pattern, '', line)
                    f.write(line)
            else:
                continue


def txt_to_csv():
    print('txt_to_csv')
    dataframe = pd.read_csv(
        'extracted_data/filtered_text_data.txt', delimiter=' ')
    dataframe.columns = ['First_Name', 'Last_Name',
                         'Month', 'Day', 'Avg Glucose Level']
    dataframe.to_csv('extracted_data/final_formatted_csv_data.csv')
