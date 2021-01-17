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


class Helper_Functions():
    def __init__(self, max_cache=None, file_cache=None, first_and_last_name=None):

        if max_cache is None:
            self.max_cache = []
        else:
            self.max_cache = max_cache

        if file_cache is None:
            self.file_cache = ""
        else:
            self.file_cache = max_cache

        if first_and_last_name is None:
            self.first_and_last_name = []
        else:
            self.first_and_last_name = first_and_last_name

    def find_correct_pages(self, header_of_correct_pages, pdf):
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

    def create_truncated_data_files_helper_function(self, metric, pages, writable_pdf, where_to_save_pdf, person):
        print('write_data_to_txt_file')
        pdfWriter = PdfFileWriter()
        person = person.replace(".pdf", "")

        for page_num in pages:
            pdfWriter.addPage(writable_pdf.getPage(page_num))

        with open(f"{where_to_save_pdf}/{person}_truncated_data_{metric}.pdf", 'wb') as f:
            pdfWriter.write(f)
            f.close()

    def write_to_extracted_data(self, metric):
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

    def filter_extracted_data(self, metric):
        print('filter_txt_data')
        for index, extracted_data_files in enumerate(sorted(os.listdir('./extracted_data'))):
            file_path = os.path.join('./extracted_data', extracted_data_files)

            if (extracted_data_files != self.file_cache and index != 0):
                self.add_last_glucose_reading(
                    file_path=f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data.txt')
            else:
                self.file_cache = extracted_data_files

            self.first_and_last_name = extracted_data_files.split('_')[0:2]

            with open(file_path, 'r') as extracted_data_files_to_edit:
                lines = extracted_data_files_to_edit.readlines()

                for index, line in enumerate(lines):
                    line = re.sub(r"[^A-Za-z0-9 ]+", '', line)

                    if (metric == 'avg'):
                        if any(x in line for x in ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')):
                            with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                                line = line.replace('180', '')
                                line = line.replace("  ", ' ')
                                line = f"{self.first_and_last_name[0]} {self.first_and_last_name[1]} " + line
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

                            if (self.max_cache != []):

                                with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                                    filtered_text_data.write(
                                        str(max(self.max_cache)) + os.linesep)

                                    self.max_cache = []

                            for month in ('Jan ', 'Feb ', 'Mar ', 'Apr ',
                                          'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '):
                                if (month in line):
                                    selected_month = month
                                    break

                            with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data.txt', "a") as filtered_text_data:
                                line = line.replace("350", '')
                                index_of_month = line.index(selected_month)
                                line = line[index_of_month:]

                                if ('am' in line):
                                    index_of_times = line.index('am') - 3
                                    line = line[0:index_of_times]
                                    line = line + os.linesep

                                filtered_text_data.write(
                                    line.strip() + os.linesep)

                        else:
                            if ("Low Glucose" in line):
                                continue
                            line = re.sub(r"[^0-9 ]", '', line)
                            line = re.sub(r"\s{2,}", " ", line)
                            line = line.strip()
                            line = line.split(" ")

                            if (line[0] == ""):
                                continue

                            if not line:
                                continue
                            else:
                                nums = [int(x) for x in line]

                            nums = [x for x in nums if (50 < x < 300)]

                            if not nums:
                                continue
                            else:
                                max_num = max(nums)

                            if (((len(nums) == 1) and ((nums[0] == 180) or (nums[0] == 70) or (nums[0] == " ")))):
                                continue

                            self.max_cache.append(max_num)

    def add_last_glucose_reading(self, file_path):
        print('add_last_glucose_reading')

        with open(file_path, "a") as filtered_text_data:
            filtered_text_data.write(
                str(max(self.max_cache)) + os.linesep)

        self.max_cache = []

    def txt_to_csv(self, metric):
        print('txt_to_csv')
        if (metric == 'avg'):
            for extracted_and_filtered_data_file in sorted(os.listdir('./extracted_and_filtered_data')):
                print(extracted_and_filtered_data_file)
                first_and_last_name = extracted_and_filtered_data_file.split('_')[
                    0:2]
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

        elif (metric == 'max'):
            for extracted_and_filtered_data_file in sorted(os.listdir('./extracted_and_filtered_data')):
                print(extracted_and_filtered_data_file)
                first_and_last_name = extracted_and_filtered_data_file.split('_')[
                    0:2]
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
