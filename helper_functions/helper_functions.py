from PyPDF2 import PdfFileReader, PdfFileWriter


def find_correct_pages(metric, pdf):
    pages = []
    for index, page in enumerate(pdf):
        if metric in page:
            pages.append(index)
    return pages


def create_new_pdf(pages, writable_pdf, where_to_save_pdf):
    pdfWriter = PdfFileWriter()

    for page_num in pages:
        pdfWriter.addPage(writable_pdf.getPage(page_num))

    with open(f"{where_to_save_pdf}/truncated_data.pdf", 'wb') as f:
        pdfWriter.write(f)
        f.close()

    return(f"{where_to_save_pdf}/truncated_data.pdf")


def trim_the_new_pdf(path_to_cut, files):
    with open(path_to_cut, "rb") as in_f:
        input_one = PdfFileReader(in_f)
        output = PdfFileWriter()
        output_two = PdfFileWriter()
        numPages = input_one.getNumPages()

        for i in range(numPages):
            page = input_one.getPage(i)
            page.cropBox.lowerLeft = (30, 820)
            page.cropBox.lowerRight = (80, 820)
            page.cropBox.upperLeft = (30, 80)
            page.cropBox.upperRight = (80, 80)

            page.trimBox.lowerLeft = (30, 820)
            page.trimBox.lowerLeft = (80, 820)
            page.trimBox.upperRight = (30, 80)
            page.trimBox.upperRight = (80, 80)
            output.addPage(page)

        with open(f"preprocessed_data/date_{files}".format(path_to_cut), "wb") as out_f:
            output.write(out_f)

        for i in range(numPages):
            page_two = input_one.getPage(i)
            page_two.cropBox.lowerLeft = (360, 820)
            page_two.cropBox.lowerRight = (410, 820)
            page_two.cropBox.upperLeft = (360, 80)
            page_two.cropBox.upperRight = (410, 80)

            page_two.trimBox.lowerLeft = (30, 820)
            page_two.trimBox.lowerLeft = (80, 820)
            page_two.trimBox.upperRight = (30, 80)
            page_two.trimBox.upperRight = (80, 80)
            output_two.addPage(page_two)

        with open(f"preprocessed_data/avg_glucose_{files}".format(path_to_cut), "wb") as out_f:
            output.write(out_f)
