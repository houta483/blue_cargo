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


def create_truncated_data_files_helper_function(metric, pages, writable_pdf, where_to_save_pdf, person):
    print('write_data_to_txt_file')
    pdfWriter = PdfFileWriter()
    full_names = []

    person = person.replace(".pdf", f"_{metric}.pdf")

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    if (metric == 'avg'):
        with open(f"{where_to_save_pdf}/truncated_data_avg_{person}", 'wb') as f:
            pdfWriter.write(f)
            f.close()

    elif (metric == 'max'):
        with open(f"{where_to_save_pdf}/truncated_data_max_{person}", 'wb') as f:
            pdfWriter.write(f)
            f.close()


def write_to_extracted_data(metric):
    # TODO ADD SOMETHING HERE SO THAT WE CAN DIFFERENTIALTE BETWEEN MAX AND AVE
    for index, files in enumerate(sorted(os.listdir('./truncated_data'))):
        file_path_to_scrape = os.path.join('./truncated_data', files)
        length_of_pdf = PdfFileReader(
            open(file_path_to_scrape, 'rb')).getNumPages()

        with pdfplumber.open(file_path_to_scrape) as pdf:
            for x in range(length_of_pdf):
                page = pdf.pages[x]
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if (x == 0):
                    first_and_last_name = text.split(' ')[0:2]
                with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data.txt", "a") as f:
                    f.write(text)


def filter_extracted_data(metric):
    print('filter_txt_data')
    for extracted_data_files in sorted(os.listdir('./extracted_data')):
        first_and_last_name = extracted_data_files.split('_')[0:2]
        file_path = os.path.join('./extracted_data', extracted_data_files)

        with open(file_path, 'r') as extracted_data_files_to_edit:
            lines = extracted_data_files_to_edit.readlines()

            for index, line in enumerate(lines):
                if (metric == 'avg'):
                    if any(x in line for x in ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')):
                        with open(f'extracted_and_filtered_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                            line = line.replace('180', '')
                            line = line.replace("  ", ' ')
                            line = f"{first_and_last_name[0]} {first_and_last_name[1]} " + line
                            line = line.strip("\n")
                            line = line.split(" ")

                            while (len(line) < 5):
                                line.append(" ")

                            if (line[4] == " "):
                                line[4] = float("NaN")

                            final_text = f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]}\n"
                            filtered_text_data.write(final_text)

                elif (metric == 'max'):
                    print(line)


def txt_to_csv():
    print('txt_to_csv')
    for extracted_and_filtered_data_file in sorted(os.listdir('./extracted_and_filtered_data')):
        print(extracted_and_filtered_data_file)
        first_and_last_name = extracted_and_filtered_data_file.split('_')[0:2]
        print('first and last name')
        print(first_and_last_name)

        file_path = os.path.join(
            './extracted_and_filtered_data', extracted_and_filtered_data_file)
        print('filepath')
        print(file_path)
        dataframe = pd.read_csv(
            file_path, delimiter=' ')

        print('dataframe')
        print(dataframe)
        dataframe.columns = ['First Name', 'Last Name',
                             'Month', 'Day', 'Avg Glucose Level']

        print('datafrom.to_csv')
        dataframe.to_csv(
            f'./final_csv_data/{first_and_last_name[0]}_{first_and_last_name[1]}_final_formatted_csv_data.csv')
