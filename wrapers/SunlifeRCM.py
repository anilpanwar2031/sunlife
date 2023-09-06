import random, string
from FileDownload import Downloader
import tika
import pandas as pd
from tika import parser
from Utilities.pdf_utils import *


def filedownload_(url):
    file_path = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".pdf"
    print(file_path)
    input_file = url.replace("%20", " ")
    print("input_file>>>>>>>>>>>>>>", input_file)
    Downloader('Revenue Cycle Management', file_path, input_file)
    return file_path

def details_scraper(file_path):
    df_li, workd = get_data_in_format(file_path)
    new_df = pd.DataFrame()
    for i in range(len(df_li)):
        for j in df_li[i].columns:
            if 'Claim #' in j or 'Client/Group No' in j:
                new_df = pd.concat([new_df, df_li[i]], axis=0)
    detail_columns = ['ServiceDate', 'Description', 'ToothNo.', 'SubmittedServices', 'SubmittedCharges',
                      'AllowedService',
                      'AllowedAmount', 'CoPay', 'Deductible', 'PPOSavings', 'PatientResp', 'RemarkCode',
                      'PlanPayment']
    drop_index = []
    new_df = new_df.fillna('')
    for j in range(new_df.shape[0]):
        for i in range(new_df.shape[1]):
            if 'Service Date' in new_df.iloc[j, :][i]:
                drop_index.append(j)
                break
            if 'TOTALS' in new_df.iloc[j, :][i]:
                drop_index.append(j)
                break
            if 'Total Patient Responsibility' in new_df.iloc[j, :][i]:
                drop_index.append(j)
                break
            if 'Client/Group No' in new_df.iloc[j, :][i]:
                drop_index.append(j)
                break

    print("new_df>>>>>>>>>>>>>>", new_df)
    print("new_df>>>>>>>>>>>>>>", len(new_df))
    if len(new_df) != 0:
        new_df.columns = detail_columns
        for j in drop_index:
            new_df.drop(j, inplace=True)
        new_df.reset_index(inplace=True)
        if 'index' in list(new_df.columns):
            new_df = new_df.drop('index', axis=1)
        for i in detail_columns:
            new_df[i] = new_df[i].str.strip()

        return new_df.to_dict('records')
    else:
        new_df = []
        return new_df


def main(data):
    """
        This function takes in a dictionary containing two lists: 'RcmEobClaimMaster' and 'RcmEobClaimDetail'.
        It modifies keys of the RcmEobClaimDetail.

        Args:
        - data: A dictionary containing two lists: 'RcmEobClaimMaster' and 'RcmEobClaimDetail'.

        Returns:
        - A modified 'data' dictionary with the changed keys in 'RcmEobClaimDetail'.
    """
    for i in range(len(data['RcmEobClaimMaster'])):
        url = data["RcmEobClaimMaster"][i]["url"].replace('%20', ' ')
        pdf_file = filedownload_(url)
        
    data['RcmEobClaimDetail'] = details_scraper(pdf_file)

    return data

#     with open("newJson.json", "w") as jsonFile:
#         json.dump(data, jsonFile, indent=4)
#
#
# with open("output_33101.json", "r") as jsonFile:
#     data = json.load(jsonFile)
# main(data)
