import tabula
import pdfplumber
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from FileDownload import Downloader
import random, string


def extract_text_coordinates(pdf_path):
    """
        Extracts text content and their coordinates from each page of a PDF.

        This function reads the specified PDF file and extracts text content along with their
        corresponding coordinates on each page. The extracted information is returned as a list
        of dictionaries, where each dictionary represents a text element with its page number,
        actual text, X-coordinate, and Y-coordinate.

        Args:
            pdf_path (str): The path to the PDF file to be processed.

        Returns:
            list: A list of dictionaries containing text elements and their coordinates.
                  Each dictionary has the following keys:
                      - 'page': Page number of the text element.
                      - 'text': The actual text content.
                      - 'cordx': X-coordinate of the text element.
                      - 'cordy': Y-coordinate of the text element.
    """

    text_list = []
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through each page of the PDF
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            page_number = page_number + 1
            # Extract the text content and its coordinates
            for element in page.extract_words(x_tolerance=1, y_tolerance=1, keep_blank_chars=True):
                text_dict = {}
                text = element["text"]
                x, y = element["x0"], element["top"]

                text_cord = f"Page {page_number + 1}: Text: {text} Coordinates: X={x}, Y={y}"
                text_dict.update({'page': page_number, 'text': text, 'cordx': x, 'cordy': y})
                text_list.append(text_dict)
    return text_list


def main(data):
    """
        Extracts specific tabular data from a PDF document, processes it, and updates a JSON file.

        This function performs the following steps:
        1. Downloads a PDF file specified in the input JSON data.
        2. Extracts text and coordinates from the PDF file.
        3. Identifies table area boundaries.
        4. Extracts tabular data from the identified area.
        5. Processes and filters the extracted data.
        6. Updates the input JSON data with the filtered tabular data.

        Args:
            data (dict): A dictionary containing JSON data. The structure should include details
                         about the PDF to process and where to save the extracted data.

        Returns:
            None: The function updates the input JSON data and writes the results to a file.
    """

    pdf_path = ("".join(random.choices(string.ascii_uppercase + string.digits, k=12)) + ".pdf")
    input_file = data["RcmEobClaimMaster"][0]["url"].replace("%20", " ")
    print("input_file>>>>>>>>>>>>>>", input_file)
    Downloader("Revenue Cycle Management", pdf_path, input_file)

    text_list = extract_text_coordinates(pdf_path)

    dfs = []
    x2 = 0
    y2 = 0
    for text_d in text_list:
        x = text_d['cordx']
        y = text_d['cordy']
        if x2 < x:
            x2 = text_d['cordx']
        if y2 < y:
            y2 = text_d['cordy']
    x2 = x2 + 20
    y2 = y2 + 20
    print("X2", x2)
    print("YYYY", y2)

    for i in range(len(text_list)):
        x1 = y1 = ''
        if 'TOOTH' in text_list[i]['text']:
            print("Line", text_list[i]['text'])
            x1 = text_list[i]['cordx']
            y1 = text_list[i]['cordy']
            page_number = text_list[i]['page']
            for j in range(i, len(text_list)):

                if page_number == text_list[j]['page']:
                    if 'TOTALS' in text_list[j]['text']:
                        page = int(text_list[j]['page'])
                        y2 = text_list[j]['cordy']
                        print(f"x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
                        tabula_dfs = tabula.read_pdf(pdf_path, guess=False, pages=page, stream=True, encoding="utf-8",
                                                     area=(y1, x1, y2, x2), multiple_tables=True)
                        df_filled = tabula_dfs[0].fillna('')
                        dfs.append(df_filled[1:])
                        break

    new_dict = []
    for td in dfs:
        tab = td.to_dict(orient='records')
        for i in range(len(tab)):
            new_dict.append(tab[i])

    filtered_data = [item for item in new_dict if item.get('OOTH') not in ('AVITY', 'or')]

    final_filtered_data = []
    for obj in filtered_data:
        new_dict = {
            "ToothOrCavity": obj["OOTH"],
            "DateOfService": obj["Unnamed: 0"],
            "ProcedureDescription": obj["Unnamed: 1"],
            "SubmittedAmount": obj["Unnamed: 2"],
            "ContractAllowance": obj["Unnamed: 3"],
            "PlanAllowance": obj["Unnamed: 4"],
            "Deductible": obj["Unnamed: 5"],
            "MemberCoins": obj["Unnamed: 6"],
            "WhatWeWillPay": obj["Unnamed: 7"],
            "WhatYouOwe": obj["Unnamed: 8"],
            "MessageCode": obj["Unnamed: 9"],
        }
        final_filtered_data.append(new_dict)

    data["RcmEobClaimDetail"] = []

    for obj in final_filtered_data:
        data["RcmEobClaimDetail"].append(obj)


    return data

#     with open("newJson.json", "w") as jsonFile:
#         json.dump(data, jsonFile, indent=4)
#
#
# with open("output_28042.json", "r") as jsonFile:
#     data = json.load(jsonFile)
# main(data)