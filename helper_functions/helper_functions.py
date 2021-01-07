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


def create_truncated_data_files_helper_function(pages, writable_pdf, where_to_save_pdf, person):
    print('write_data_to_txt_file')
    pdfWriter = PdfFileWriter()
    full_names = []

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    with open(f"{where_to_save_pdf}/truncated_data_{person}", 'wb') as f:
        pdfWriter.write(f)
        f.close()


def write_to_extracted_data():
    for index, files in enumerate(os.listdir('./truncated_data')):
        # TODO -> USER MUST SUBMIT A FIRST AND LAST NAME
        file_path_to_scrape = os.path.join('./truncated_data', files)
        length_of_pdf = PdfFileReader(
            open(file_path_to_scrape, 'rb')).getNumPages()

        with pdfplumber.open(file_path_to_scrape) as pdf:
            for x in range(length_of_pdf):
                page = pdf.pages[x]
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if (x == 0):
                    first_and_last_name = text.split(' ')[0:2]
                    # full_names.append(first_and_last_name)
                with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data.txt", "a") as f:
                    # THIS IS WHERE DUPLICATION IS HAPPENING
                    f.write(text)


def filter_extracted_data():
    print('filter_txt_data')
    for extracted_data_files in os.listdir('./extracted_data'):
        first_and_last_name = extracted_data_files.split('_')[0:2]
        file_path = os.path.join('./extracted_data', extracted_data_files)
        with open(file_path, 'r') as extracted_data_files_to_edit:
            lines = extracted_data_files_to_edit.readlines()

            for index, line in enumerate(lines):
                # TODO: FOR EFFICIENCY, I MIGHT BE ABLE TO USE A DICT HERE INSTEAD OF A LOOP
                if any(x in line for x in ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')):
                    with open(f'extracted_and_filtered_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                        line = line.replace('180', '')
                        line = line.replace("  ", ' ')
                        line = f"{first_and_last_name[0]} {first_and_last_name[1]} " + line
                        filtered_text_data.write(line)


def txt_to_csv():
    print('txt_to_csv')
    for extracted_and_filtered_data_file in os.listdir('./extracted_and_filtered_data'):
        first_and_last_name = extracted_and_filtered_data_file.split('_')[0:2]
        file_path = os.path.join(
            './extracted_and_filtered_data', extracted_and_filtered_data_file)
        dataframe = pd.read_csv(
            file_path, delimiter=' ')
        dataframe.columns = ['First Name', 'Last Name',
                             'Month', 'Day', 'Avg Glucose Level']
        dataframe.to_csv(
            f'./final_csv_data/{first_and_last_name[0]}_{first_and_last_name[1]}_final_formatted_csv_data.csv')
