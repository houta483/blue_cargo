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
    def __init__(self, max_cache=None, min_cache=None, file_cache=None, first_and_last_name=None):

        if max_cache is None:
            self.max_cache = []
        else:
            self.max_cache = max_cache

        if min_cache is None:
            self.min_cache = []
        else:
            self.min_cache = min_cache

        if file_cache is None:
            self.file_cache = ""
        else:
            self.file_cache = max_cache

        if first_and_last_name is None:
            self.first_and_last_name = []
        else:
            self.first_and_last_name = first_and_last_name

    def find_correct_pages(self, metric, pdf):
        print('find_corect_pages')
        pages = []

        if (metric == 'avg'):
            header_of_correct_pages = "Weekly Summary"
        elif ((metric == 'max') or (metric == 'min')):
            header_of_correct_pages = 'Daily Log'
            for index, page in enumerate(pdf):
                if 'Weekly Summary' in page:
                    pages.append(index)
                    break

        for index, page in enumerate(pdf):
            if header_of_correct_pages in page:
                pages.append(index)

        return pages

    def create_truncated_data_files_helper_function(self, metric, pages, text_from_original_data_file, where_to_save_pdf, arg_we_will_use_to_get_person_and_date_data):
        print('write_data_to_txt_file')
        pdfWriter = PdfFileWriter()
        name_and_date = arg_we_will_use_to_get_person_and_date_data.replace(
            ".pdf", "")

        for page_num in pages:
            pdfWriter.addPage(text_from_original_data_file.getPage(page_num))

        with open(f"{where_to_save_pdf}/{name_and_date}_truncated_data_{metric}.pdf", 'wb') as f:
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
                    filtered = page.filter(lambda x: x.get("upright") == True)
                    text = filtered.extract_text()

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

                    if (x == 0 and metric == 'min'):
                        first_and_last_name = text.split(' ')[0:2]

                    elif (metric == 'min'):
                        with open(f"extracted_data/{first_and_last_name[0]}_{first_and_last_name[1]}_extracted_data_min.txt", "a") as f:
                            f.write(text)

    def filter_extracted_data(self, metric):
        print('filter_txt_data')

        # LOOKS THROUGH EACH FILE IN THE EXTRACTED DATA FOLDER
        for index, extracted_data_files in enumerate(sorted(os.listdir('./extracted_data'))):
            file_path = os.path.join('./extracted_data', extracted_data_files)

            # NEED TO HAVE THE FILE CACHE SO THAT WE ADD THE LAST VALUES TO THE PREVIOUS FILE WHEN WE GO ONTO ANOTHER PERSON
            self.add_glucose_reading_or_set_file_cache(
                extracted_data_files, index, metric)

            self.first_and_last_name = extracted_data_files.split('_')[0:2]

            with open(file_path, 'r') as extracted_data_files_to_edit:
                lines = extracted_data_files_to_edit.readlines()

                # LOOPS THROUGH EACH LINE IN THE FILE
                for index, line in enumerate(lines):
                    line = re.sub(r"[^A-Za-z0-9 ]+", '', line)

                    if (metric == 'avg'):
                        self.filter_and_write_extracted_data_avg(line, metric)

                    elif (metric == 'max'):
                        # SEE IF WE SHOULD APPEND DATE OR APPEND GLUCOSE READING
                        self.when_there_is_a_new_month_write_glucose_reading_and_when_there_is_not_a_new_month_add_glucose_reading_to_cache(
                            line, metric)

                    elif (metric == 'min'):
                        self.when_there_is_a_new_month_write_glucose_reading_and_when_there_is_not_a_new_month_add_glucose_reading_to_cache(
                            line, metric)

    def add_glucose_reading_or_set_file_cache(self, extracted_data_files, index, metric):
        # ADDS THE FINAL GLUCOSE READING BEFORE HEADING ON TO THE NEXT FILE
        if ((extracted_data_files != self.file_cache) and (index != 0) and (metric == 'max' or metric == 'min')):
            if (metric == 'max'):
                measure = max
                cache = self.max_cache
            elif (metric == 'min'):
                measure = min
                cache = self.min_cache

            print('add_final_glucose_reading')
            file_path = f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt'

            with open(file_path, "a") as filtered_text_data:
                filtered_text_data.write(
                    str(measure(cache)) + os.linesep)

            self.max_cache = []
            self.min_cache = []
            self.file_cache = extracted_data_files

        else:
            self.file_cache = extracted_data_files

    def filter_and_write_extracted_data_avg(self, line, metric):
        is_it_a_date_line = True if (any(x in line for x in (
            'Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '))) else False

        if (is_it_a_date_line):
            with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt', "a") as filtered_text_data:
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

    def when_there_is_a_new_month_write_glucose_reading_and_when_there_is_not_a_new_month_add_glucose_reading_to_cache(self, line, metric):
        print('when_there_is_a_new_month_write_glucose_reading_and_when_there_is_not_a_new_month_add_glucose_reading_to_cache')

        cache = self.max_cache if metric == 'max' else self.min_cache

        the_cache_is_empty_or_filled_with_default = True if ((all(x == 0 for x in cache) and (
            metric == 'max')) or (all(x == 999 for x in cache) and (metric == 'min'))) else False

        is_it_a_date_line = True if (any(x in line for x in (
            'Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '))) else False

        # GETS THE MONTH LINES - IF THERE IS A MONTH, THEN THE PIPELINE MUST EITHER: START A NEW MONTH LINE, ADD THE GLUCOSE VALUE FOR THAT MONTH, OR ADD A BLANK LINESTEP.
        if (is_it_a_date_line):

            # IF THERE IS SOMETHING IN THE CACHE...
            if (cache != []):
                # ...AND THE VALUES ARE ALL THE DEFUALT PLACEHOLDERS, THEN WRITE A BLANK VALUE/LINESTEP
                if (the_cache_is_empty_or_filled_with_default):
                    if (os.path.exists(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt')):
                        with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt', "a") as filtered_text_data:
                            filtered_text_data.write(os.linesep)

                # ...AND IT IS NOT ALL DEFUALT PLACEHOLDERS, THEN WRITE THE GLUCOSE VALUE FOR THE PREVIOUS DAY LINE
                else:
                    with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt', "a") as filtered_text_data:
                        if (metric == 'max'):
                            filtered_text_data.write(
                                str(max(self.max_cache)) + os.linesep)
                            self.max_cache = []
                        elif (metric == 'min'):
                            filtered_text_data.write(
                                str(min(self.min_cache)) + os.linesep)
                            self.min_cache = []

            # NOW, THAT WE'VE TAKEN CARE OF GLUCOSE READINGS FOR PREVIOUS DAY, LET'S MOVE ONTO THE LINE FOR THE NEXT DAY
            filtered_data_from_month_line = self.return_the_date_line(
                line=line)

            # LET'S WRITE THAT DATE LINE WE GOT TO THE EXTRACTED AND FILTERED DATA
            with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt', "a") as extracted_and_filtered_text_data_file:
                extracted_and_filtered_text_data_file.write(
                    filtered_data_from_month_line)
        else:
            # IF IT IS A LINE THAT DOES NOT CONTAIN A NEW DAY READING, FILTER FOR GLUCOSE VALUES TO ADD TO THE QUEUE
            returned_value_from_filter_for_each_line_max_or_min = self.filter_for_each_line_max_or_min(
                line, metric)

            cache.append(returned_value_from_filter_for_each_line_max_or_min)

    def return_the_date_line(self, line):
        print('write the month into extracted and filtered data')

        # GETS THE SPECIFIC MONTH THAT IS IN THAT LINE
        for month in ('Jan ', 'Feb ', 'Mar ', 'Apr ',
                      'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '):
            if (month in line):
                selected_month = month
                break

        # FILTERS THE LINE UNTIL WE GET THE MONTH AND DAY OF MONTH ONLY
        filtered_date_line = line.replace("350", '')
        index_of_month = filtered_date_line.index(selected_month)
        filtered_date_line = filtered_date_line[index_of_month:]

        if ('am' in filtered_date_line):
            index_of_times = filtered_date_line.index('am') - 3
            filtered_date_line = filtered_date_line[0:index_of_times]
            filtered_date_line = f"{self.first_and_last_name[0]} {self.first_and_last_name[1]} " + \
                filtered_date_line
            filtered_date_line = filtered_date_line + " "
            filtered_date_line = filtered_date_line.replace("  ", " ")

        else:
            filtered_date_line = f"{self.first_and_last_name[0]} {self.first_and_last_name[1]} " + filtered_date_line.strip(
            ) + " "

        return filtered_date_line

    # THIS FUNCTION TAKES A NON-MONTH LINE AND OUTPUTS THE MAX OR MIN GLUCOSE VALUE
    def filter_for_each_line_max_or_min(self, line, metric):
        # FILTET_FOR_EACH_LINE_MAX_OR_MIN
        default_place_holder_value_to_append = 0 if (metric == 'max') else 999

        if (("Glucose" in line) or ('PostMeal' in line) or ('14 Days' in line) or ('pm' in line) or ('TestDaily') in line):
            return default_place_holder_value_to_append

        if ((line == '110') or (line == "70") or (line == '0')):
            return default_place_holder_value_to_append

        line = re.sub(r"[^0-9 ]", '', line)
        line = re.sub(r"\s{2,}", " ", line)
        line = line.strip()
        line = line.split(" ")

        # TODO -> Clean this up
        if (line[0] == ""):
            return default_place_holder_value_to_append

        if not line:
            return default_place_holder_value_to_append
        else:
            nums = [int(x) for x in line if x[0] != "0"]

        nums = [x for x in nums if (50 < x < 300)]

        if not nums:
            return default_place_holder_value_to_append
        elif(nums[0] == 180):
            nums = nums[1:]

        if not nums:
            return default_place_holder_value_to_append
        else:
            max_or_min_nums = max(nums) if (metric == 'max') else min(nums)

        if ((nums[0] == 70) or (nums[0] == " ")):
            return default_place_holder_value_to_append

        return max_or_min_nums

    def txt_to_csv(self, metric):
        print('txt_to_csv')

        cache = self.max_cache if metric == 'max' else self.min_cache
        column_names = ['First Name', 'Last Name',
                        'Month', 'Day', f"{metric} Glucose Level"]

        # APPEND THE FINAL GLUCOSE READING ONTO THE FINAL EXTRACTED AND FILTERED TXT FILE
        if ((metric == 'max') or (metric == 'min')):
            max_or_min = max if (metric == 'max') else min
            with open(f'extracted_and_filtered_data/{self.first_and_last_name[0]}_{self.first_and_last_name[1]}_extracted_and_filtered_data_{metric}.txt', "a") as filtered_text_data:
                filtered_text_data.write(
                    str(max_or_min(cache)) + os.linesep)

        # CONVERT TXT FILE FROM EXTRACTED AND FILTERED TO CSV
        for extracted_and_filtered_data_file in sorted(os.listdir('./extracted_and_filtered_data')):
            first_and_last_name = extracted_and_filtered_data_file.split('_')[
                0: 2]

            file_path = os.path.join(
                './extracted_and_filtered_data', extracted_and_filtered_data_file)

            dataframe = pd.read_csv(
                file_path, delimiter=' ', names=column_names)

            dataframe.to_csv(
                f'./final_csv_data/{first_and_last_name[0]}_{first_and_last_name[1]}_final_formatted_csv_data_{metric}.csv', index=False)
