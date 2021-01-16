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


def find_correct_pages(header_of_correct_pages, pdf):
    print('find_corect_pages')
    pages = []

    if (header_of_correct_pages == 'Daily Log'):
        for index, page in enumerate(pdf):
            if 'Weekly Summary' in page:
                pages.append(index)
                break

    for index, page in enumerate(pdf):
        if header_of_correct_pages in page:
            pages.append(index)
    return pages


def create_truncated_data_files_helper_function(metric, pages, writable_pdf, where_to_save_pdf, person):
    print('write_data_to_txt_file')
    pdfWriter = PdfFileWriter()
    person = person.replace(".pdf", "")

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    with open(f"{where_to_save_pdf}/{person}_truncated_data_{metric}.pdf", 'wb') as f:
        pdfWriter.write(f)
        f.close()


def write_to_extracted_data(metric):
    # TODO ADD SOMETHING HERE SO THAT WE CAN DIFFERENTIALTE BETWEEN MAX AND AVE
    # TODO FIND A BETTER WAY TO GET THE CORRECT NAMES (add the name from avg)
    for index, files in enumerate(sorted(os.listdir('./truncated_data'))):
        file_path_to_scrape = os.path.join('./truncated_data', files)
        length_of_pdf = PdfFileReader(
            open(file_path_to_scrape, 'rb')).getNumPages()

        with pdfplumber.open(file_path_to_scrape) as pdf:

            for x in range(length_of_pdf):
                page = pdf.pages[x]
                text = page.extract_text(x_tolerance=3, y_tolerance=3)

                if (x == 0 and metric == 'avg'):
                    first_and_last_name = text.split(' ')[0:2]
                    with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data_avg.txt", "a") as f:
                        f.write(text)

                elif (x != 0 and metric == 'avg'):
                    with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data_avg.txt", "a") as f:
                        f.write(text)

                if (x == 0 and metric == 'max'):
                    first_and_last_name = text.split(' ')[0:2]

                elif (metric == 'max'):
                    with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data_max.txt", "a") as f:
                        f.write(text)


def filter_extracted_data(metric):
    print('filter_txt_data')
    for extracted_data_files in sorted(os.listdir('./extracted_data')):
        first_and_last_name = extracted_data_files.split('_')[0:2]
        file_path = os.path.join('./extracted_data', extracted_data_files)

        with open(file_path, 'r') as extracted_data_files_to_edit:
            lines = extracted_data_files_to_edit.readlines()

            for index, line in enumerate(lines):
                print(line)
                line = re.sub(r"[^A-Za-z0-9 ]+", '', line)

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
                    selected_month = ''

                    if any(x in line for x in ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')):
                        for month in ('Jan ', 'Feb ', 'Mar ', 'Apr ',
                                      'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '):
                            if (month in line):
                                selected_month = month
                                break

                        with open(f'extracted_and_filtered_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                            line = line.replace("350", '')
                            index_of_month = line.index(selected_month)
                            line = line[index_of_month:]

                            if ('am' in line):
                                index_of_times = line.index('am') - 3
                                line = line[0:index_of_times]
                                line = line + os.linesep

                            filtered_text_data.write(line.strip() + os.linesep)

                    else:
                        if ("Low Glucose" in line):
                            continue
                        # ONLY NUMBERS
                        line = re.sub(r"[^0-9 ]", '', line)
                        # REMOVE WHITESPACE
                        line = re.sub(r"\s{2,}", " ", line)

                        line = line.strip()
                        # SPLIT
                        line = line.split(" ")

                        if (line[0] == ""):
                            continue

                        if not line:
                            continue
                        else:
                            nums = [int(x) for x in line]

                        # remove nums greater than 300 and less than 50
                        nums = [x for x in nums if (50 < x < 300)]

                        if not nums:
                            continue
                        else:
                            max_num = max(nums)

                        if (((len(nums) == 1) and ((nums[0] == 180) or (nums[0] == 70) or (nums[0] == " ")))):
                            continue

                        with open(f'extracted_and_filtered_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                            filtered_text_data.write(str(max_num) + os.linesep)


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
