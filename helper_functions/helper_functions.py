import fitz
import os
from PIL import Image
from string import ascii_lowercase
from PyPDF2 import PdfFileReader, PdfFileWriter
import pytesseract


def find_correct_pages(metric, pdf):
    print('find_corect_pages')
    pages = []
    for index, page in enumerate(pdf):
        if metric in page:
            pages.append(index)
    return pages


def create_new_pdf(pages, writable_pdf, where_to_save_pdf, person):
    print('create_new_pdf')
    pdfWriter = PdfFileWriter()

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    with open(f"{where_to_save_pdf}/truncated_data_{person}.pdf", 'wb') as f:
        pdfWriter.write(f)
        f.close()

    pdffile = f"{where_to_save_pdf}/truncated_data_{person}.pdf"

    for index in range(len(pages)):
        doc = fitz.open(pdffile)
        page = doc.loadPage(index)
        pix = page.getPixmap()
        output = f"preprocessed_data/{ascii_lowercase[index]}_{person}_outfile_page_number_{index}.png"
        pix.writePNG(output)


def crop_jpg(person):
    print('crop_jpg')
    parent_folder = 'preprocessed_data'

    for index, files in enumerate(os.listdir(parent_folder)):
        file_path_to_crop = os.path.join(parent_folder, files)
        im = Image.open(file_path_to_crop)

        left_date = 30
        top_date = 100
        right_date = 80
        bottom_date = 680

        left_glucose = 360
        top_glucose = 100
        right_glucose = 410
        bottom_glucose = 680

        im1 = im.crop((left_date, top_date, right_date, bottom_date))
        im2 = im.crop((left_glucose, top_glucose,
                       right_glucose, bottom_glucose))

        imgs = [im1, im2]

        for indx, img in enumerate(imgs):
            if (indx == 0):
                img.save(
                    f"ocr_jpg_data/{ascii_lowercase[len(ascii_lowercase) - (index + 1)]}_{person}_date_{index}.jpg", "JPEG", quality=95)
            elif (indx == 1):
                img.save(
                    f"ocr_jpg_data/{ascii_lowercase[len(ascii_lowercase) - (index + 1)]}_{person}_glucose_{index}.jpg", "JPEG", quality=95)

        widths, heights = zip(*(i.size for i in imgs))
        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0

        for im in imgs:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        new_im.save(
            f"ocr_jpg_data/{ascii_lowercase[len(ascii_lowercase) - (index + 1)]}_{person}_date_and_glucose_{index}.jpg", "JPEG", quality=95)


def compile_text(extacted_data_folder):
    compiled_text = []

    for files in sorted(os.listdir(extacted_data_folder)):
        file_path_to_scrape = os.path.join(extacted_data_folder, files)
        text = str(
            ((pytesseract.image_to_string(Image.open(file_path_to_scrape)))))
        text = text.replace('-\n', '')
        text = text.replace('\n', '')
        text = text.replace('‘', '')
        text = text.replace('\x0c', '')
        compiled_text.append(text)
        print(compiled_text)

    return compiled_text


def extend_months(days, months):
    regular_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month = ''

    difference_in_length_between_months_and_days = len(days) - len(months)

    # CREATE PLACEHOLDERS
    for x in range(difference_in_length_between_months_and_days):
        months.append('PLACEHOLDER')

    # LOOP THROUGH TO TAKE CARE OF MISSING MONTHS IN THE MIDDLE
    for index, day in enumerate(days):
        current_month = f"{months[index]}"
        if (index + 1 == len(days)):
            print('broken')
            continue

        # FOR DECEMBER
        if (days[index] == 31 and current_month == "Dec"):
            print('This is a new year')
            index_of_place_holder = months.index('PLACEHOLDER')
            months[index_of_place_holder] = 'Jan'

        # FOR OTHER MONTHS
        elif (days[index] > 27 and days[index + 1] == 1):
            index_of_current_month = regular_months.index(current_month)
            next_month = f"{regular_months[index_of_current_month+1]}"
            months.insert(index + 1, next_month)

    # FOR MISSING MONTHS AT THE END
    if (months.count('PLACEHOLDER') > 0):
        index_of_first_placeholder = months.index('PLACEHOLDER')
        number_of_place_holders = months.count('PLACEHOLDER')

        for x in range(number_of_place_holders):
            months[index_of_first_placeholder +
                   x] = months[index_of_first_placeholder - 1]

    return(days, months)
