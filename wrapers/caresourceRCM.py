
def main(data):

    data['RcmEobClaimMaster'][0]['PatientName'] = data['RcmEobClaimMaster'][0]['PatientName'].replace(',', '')
    data['RcmEobClaimMaster'][0]['ProviderName'] = data['RcmEobClaimMaster'][0]['ProviderName'].replace(',', '')

    return data
