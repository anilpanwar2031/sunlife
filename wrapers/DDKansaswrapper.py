from Utilities.pdf_utils import *
from FileDownload import Downloader
from mapPDF import mapEligibilityPatientVerification
from typing import Iterable
import re
from collections import defaultdict
from datetime import datetime

def changeNone(text):
    if(text=="None" or text=="N/A" or text==None):
        return ""
    else:
        return text
def calculate_difference(a,b):
    if(a=="" or a==None):
        a="0.0"
    if(b=="" or b==None):
        b="0.0"
    a=a.replace(",", "").replace("N/A", "0").replace("$", "")
    b=b.replace(",", "").replace("N/A", "0").replace("$", "")
    difference=f'${float(a)-float(b)}'
    if(difference=="$0.00"): return "0.00"
    return f'${round(float(a)-float(b) , 2)}'
def getsum(a,b):
    if(a=="" or a==None):
        a="0.0"
    if(b=="" or b==None):
        b="0.0"
    a=a.replace(",", "").replace("N/A", "0").replace("$", "")
    b=b.replace(",", "").replace("N/A", "0").replace("$", "")
    return f'${float(a)+float(b)}'



def main(Scraperdata, request):

    patientdata = request.get("PatientData")[0]
    EligibilityPatient = Scraperdata.get("EligibilityPatientVerification")
    EligibilityMaximiums = Scraperdata.get("EligibilityMaximums")
    EligibilityDEductible = Scraperdata.get("EligibilityDeductible")
    EligibilityBenefitsData = Scraperdata.get("EligibilityBenefits")
    EligibilityTreatmentHistory = Scraperdata.get("EligibilityServiceTreatmentHistory")
    EligibilityOtherProvisions = Scraperdata.get("EligibilityOtherProvisions")


    EligibilityPatientVerification=mapEligibilityPatientVerification()
    EligibilityMaximums=[]
    EligibilityDeductiblesProcCode=[]
    EligibilityServiceTreatmentHistory=[]
    TreatmentHistorySummary=[]
    EligibilityBenefits=[]
  
    patientdata = request.get("PatientData")[0]
    details_to_merge = Scraperdata["EligibilityPatientVerification"][-1]
    

    # PBirthdate = patientdata.get("BirthDate")
    date_format = "%m/%d/%Y"
    PBirthdate = datetime.strptime(patientdata.get("BirthDate"), date_format)
    # print(PBirthdate)

    
    matching_dict = next((entry for entry in Scraperdata["EligibilityPatientVerification"] if datetime.strptime(entry.get("BirthDate"), date_format) == PBirthdate), None)
    # print(matching_dict)

    if matching_dict is not None:
        matching_dict.update(details_to_merge)
        # print(matching_dict)
    else:
        # Handle the case when matching_dict is None
        print("No matching dictionary found.")

    EligibilityPatientVerification.update(
        {
        "FamilyMemberId":patientdata.get("SubscriberId", ''),
        "SubscriberId":patientdata.get("SubscriberId"),
        "SubscriberName":patientdata.get("SubscriberFirstName")+" "+patientdata.get("SubscriberLastName"),
        "FamilyMemberName":patientdata.get("LastName")+", "+patientdata.get("FirstName").upper(),
        "FamilyMemberDateOfBirth":patientdata.get("BirthDate"),
        "Relationship":matching_dict.get("Relationship"),
        "SubscriberDateOfBirth":patientdata.get("SubscriberBirthDate"),
        "FamilyMemberEffectiveDate":matching_dict.get("EligibilityDate"),
        "FamilyMemberEndDate":matching_dict.get("TerminationDate"),
        "ClaimMailingAddress":matching_dict.get("Claimaddress"),
        "ClaimsAddress":matching_dict.get("Claimaddress"),
        "InsuranceCalendarOrFiscalPolicyYear":matching_dict.get("Policyyearbegins"),
        "GroupName":matching_dict.get("InsurancePlan"),
        "GroupNumber":matching_dict.get("GroupNumber"),
        "FamilyMemberWaitingPeriod":matching_dict.get("WaitingperiodforBasicService")+", "+matching_dict.get("WaitingperiodforMajorService"),
        "InNetworkOutNetwork":"In Network",
        "oonBenefits":"Yes",
        "AlternativebenefitProvision":matching_dict.get("AlternativebenefitProvision"),
        "EligibilityStatus":"Active",
        "MissingToothClause":matching_dict.get("MissingtoothClouse"),
        "AdultOrthodonticCovered":matching_dict.get("AdultOrthodonticCovered"),
        "DependentChildCoveredAgeLimit":matching_dict.get("Dependentstoage"),
        "DependentStudentAgeLimit":matching_dict.get("FullTimeStudent")
        }
    )
    
    individualannualdeductible = ""
    calendarfamilydeductible = ""
    annualdeductible = matching_dict.get("PolicyDeductible")
    if 'individual' in annualdeductible:
        deductible = annualdeductible.split('individual')
        if len(deductible) > 1:
            individualannualdeductible = deductible[0].strip()
            calendarfamilydeductible = deductible[1].replace('family','').strip()

    EligibilityPatientVerification.update({"IndividualAnnualDeductible":individualannualdeductible})
    EligibilityPatientVerification.update({"IndividualAnnualDeductibleMet":matching_dict.get("IndividualAnnualDeductibleMET")})
    EligibilityPatientVerification.update({"IndividualAnnualDeductibleRemaining":calculate_difference(EligibilityPatientVerification.get("IndividualAnnualDeductible").strip(),EligibilityPatientVerification.get("IndividualAnnualDeductibleMet").strip())})

    EligibilityPatientVerification.update({"FamilyAnnualDeductible":calendarfamilydeductible.replace('/','').strip()})
    EligibilityPatientVerification.update({"FamilyAnnualDeductibleMet":matching_dict.get("CalendarFamilyDeductibleMET")})
    EligibilityPatientVerification.update({"FamilyAnnualDeductibleMet":calculate_difference(EligibilityPatientVerification.get("FamilyAnnualDeductible").strip(),EligibilityPatientVerification.get("FamilyAnnualDeductibleMet").strip())})
   
    individualannualmaxbenefit = ""    
    annualbenefit = matching_dict.get("PolicyMax")
    if 'Indiv:' in annualbenefit:
        deductible = annualbenefit.split('Indiv:')[1].split('/')[0]        
        individualannualmaxbenefit = deductible
    
    EligibilityPatientVerification.update({"IndividualAnnualMaximumBenefits":individualannualmaxbenefit.strip()})
    EligibilityPatientVerification.update({"IndividualAnnualBenefitsUsedtoDate":matching_dict.get("DentalBenefitUsedtoDate")})
    EligibilityPatientVerification.update({"IndividualAnnualRemainingBenefit":matching_dict.get("DentalRemainingBenefitAvailable")})


    EligibilityPatientVerification.update({"OrthodonticLifetimeBenefit":matching_dict.get("OrthodonticlifetimeBenefit").strip()})
    EligibilityPatientVerification.update({"OrthodonticLifetimeRemainingBenefit":matching_dict.get("OrthodonticRemainingBenefit").strip()})



    # EligibilityPatientVerification.update({"FamilyMemberWaitingPeriod":"NONE"})


    EligibilityMaximums.append({
                "Type":  "Lifetime Maximum",
                "Network": "In Network",
                "Amount": EligibilityPatientVerification.get("IndividualLifetimeMaximumBenefits"),
                "Remaining": EligibilityPatientVerification.get("IndividualLifetimeRemainingBenefit"),
                "Used": EligibilityPatientVerification.get("IndividualLifetimeBenefitsUsedtoDate"),
                "ServiceCategory": "",
                "BenefitPeriod": "",
                "Family_Individual": "Individual"
            })
    EligibilityMaximums.append({
                "Type":  "Annual Maximum",
                "Network": "In Network",
                "Amount": EligibilityPatientVerification.get("IndividualAnnualMaximumBenefits"),
                "Remaining": EligibilityPatientVerification.get("IndividualAnnualRemainingBenefit"),
                "Used": EligibilityPatientVerification.get("IndividualAnnualBenefitsUsedtoDate"),
                "ServiceCategory": "",
                "BenefitPeriod": "",
                "Family_Individual": "Individual"
            })     
    EligibilityMaximums.append({
                "Type":  "Orthodontic Lifetime",
                "Network": "In Network",
                "Amount": EligibilityPatientVerification.get("OrthodonticLifetimeBenefit"),
                "Remaining": EligibilityPatientVerification.get("OrthodonticLifetimeRemainingBenefit"),
                "Used": EligibilityPatientVerification.get("OrthodonticLifetimeBenefitUsedtoDate"),
                "ServiceCategory": "",
                "BenefitPeriod": "",
                "Family_Individual": "Individual"
            })  
       


    EligibilityDeductiblesProcCode.append({
                "Type":  "Annual Deductible",
                "Network": "In Network",
                "Amount": EligibilityPatientVerification.get("IndividualAnnualDeductible"),
                "Remaining": EligibilityPatientVerification.get("IndividualAnnualDeductibleRemaining"),
                "Used": EligibilityPatientVerification.get("IndividualAnnualDeductibleMet"),
                "ServiceCategory": "",
                "BenefitPeriod": "",
                "Family_Individual": "Individual"
            }) 
    EligibilityDeductiblesProcCode.append({
                "Type":  "Annual Deductible",
                "Network": "In Network",
                "Amount": EligibilityPatientVerification.get("FamilyAnnualDeductible"),
                "Remaining": EligibilityPatientVerification.get("FamilyAnnualDeductibleRemaining"),
                "Used": EligibilityPatientVerification.get("FamilyAnnualDeductibleMet"),
                "ServiceCategory": "",
                "BenefitPeriod": "",
                "Family_Individual": "Family"
            }) 
  

    codes = [
            {"code":"D0150","search":"COMPREHENSIVE ORAL EVALUATION NEW/ESTABL"},
            {"code":"D0120","search":"PERIODIC ORAL EVALUATION-ESTABLISHED PT"},
            {"code":"D0140","search":"LIMITED ORAL EVALUATION -PROBLEM FOCUSED"}, 
            {"code":"D0170","search":"RE-EVALUATION-LIMITED, PROBLEM FOCUSED"}, # no found decsription
            {"code":"D9110","search":"PALLIATIVE TREATMENT OF DENTAL PAIN"}, # no found decsription
            {"code":"D0220","search":"INTRAORAL PERIAPICAL 1ST RADIOGRAPH"}, # no found decsription
            {"code":"D0230","search":"INTRAORAL PERIAPICAL ADDITIONAL IMAGE"}, 
            {"code":"D0272","search":"BITEWINGS - TWO RADIOGRAPHIC IMAGES"},
            {"code":"D0274","search":"BITEWINGS - FOUR RADIOGRAPHIC IMAGES"},
            {"code":"D0210","search":"INTRAORAL COMPRE SERIES OF RADIOGRAPHS"},
            {"code":"D0330","search":"PANORAMIC RADIOGRAPHIC IMAGE"},
            {"code":"D0340","search":"PANORAMIC RADIOGRAPHIC IMAGE"},
            {"code":"D7880","search":"OCCLUSAL ORTHOTIC DEVICE, BY REPORT"},
            {"code":"D4210","search":"GINGIVECTOMY/GINGIVOPLASTY-4+ PER QUAD"},
            {"code":"D4211","search":"GINGIVECTOMY/GINGIVOPLASTY 1-3 TEETH QUA"},
            {"code":"D7280","search":"EXPOSURE OF AN UNERUPTED TOOTH"},
            {"code":"D7283","search":"PLACEMENT OF DEVICE TO FACILITATE ERUPTI"},
            {"code":"D7320","search":"ALVEOLOPLASTY, NO EXTRACTIONS - PER QUAD"},
            {"code":"D8020","search":"LIMITED ORTHO TREATMENT - TRANSITIONAL"},
            {"code":"D8040","search":"LIMITED ORTHO TREATMENT - ADULT"},
            {"code":"D8080","search":"COMPREHENSIVE ORTHODONTICS-ADOLESCENT"},
            {"code":"D8090","search":"COMPREHENSIVE ORTHODONTICS - ADULT"},
            {"code":"D8703","search":"REPLACEMENT OF LOST/BROKEN RETAINER-MAX"},
            {"code":"D8704","search":"REPLACEMENT OF LOST/BROKEN RETAINER-MAND"},
            {"code":"D7321","search":"ALVEOLOPLASTY, NO EXTRACTIONS- 1-3 TEETH"},
            {"code":"D0240","search":"INTRAORAL-OCCLUSAL RADIOGRAPHIC IMAGE"}, 
            {"code":"D1110","search":"PROPHYLAXIS - ADULT"},
            {"code":"D7960","search":"FRENECTOMY"},
            {"code":"D1120","search":"PROPHYLAXIS - CHILD"},
            {"code":"D1206","search":"TOPICAL APPLICATION OF FLUORIDE VARNISH"},
            {"code":"D1208","search":"TOPICAL APPLICATION OF FLUORIDE"},
            {"code":"D1351","search":"SEALANT PER TOOTH"},
            {"code":"D1354","search":"APPLICATION OF CARIES ARRESTING MEDICAME"},
            {"code":"D1516","search":"SPACE MAINTAINER-FIXED-BILATERAL, MAXILL"},
            {"code":"D1517","search":"SPACE MAINTAINER-FIXED-BILATERAL, MANDIB"},
            {"code":"D2140","search":"AMALGAM - ONE SURFACE, PRIMARY/PERMANENT"},
            {"code":"D2150","search":"AMALGAM TWO SURFACES, PRIMARY/PERMANENT"},
            {"code":"D2160","search":"AMALGAM THREE SURFACES PRIMARY/PERMANENT"},
            {"code":"D2161","search":"AMALGAM FOUR/MORE SURFACES, PRIM/PERM"},
            {"code":"D2391","search":"RESIN COMPOSITE - ONE SURFACE POSTERIOR"},
            {"code":"D2392","search":"RESIN COMPOSITE - TWO SURFACE POSTERIOR"},
            {"code":"D2393","search":"RESIN COMPOSITE- THREE SURFACE POSTERIOR"},
            {"code":"D2394","search":"RESIN COMPOSITE-FOUR+ SURFACE POSTERIOR"},     
            {"code":"D7140","search":"EXTRACTION-ERUPTED TOOTH OR EXPOSED ROOT"}, 
            {"code":"D3220","search":"THERAPEUTIC PULPOTOMY-EXCL FINAL RESTORA"}, 
            {"code":"D2930","search":"PREFAB STAINLESS STEEL CROWN - PRIMARY"}, 
            {"code":"D2933","search":"PREFAB STAINLESS STEEL CROWN WITH RESIN"}, 
            {"code":"D2934","search":"PREFAB ESTHETIC COATED STAINLESS CROWN"}, 
            {"code":"D9230","search":"INHALATION OF NITROUS OXIDE / ANALGESIA"} 
        ]
    

    translation_table = str.maketrans('', '', ' -')
    #  To get uniques procedure codes from EligibilityTreatmentHistory  
    result = defaultdict(lambda: defaultdict(list))   
    

    for item in codes:
        if item.get("code") and item.get("search"):  # only proceed if both fields are present
            limitation = ""
            Benefits = ""
            Agelimit = ""
            waitperiod = ""
            deductible = ""
            agelimit = ""
            code = item.get("code")
            # print(code)
            descriptionfromcode = item.get("search") 

            for searchItem in EligibilityBenefitsData:
                dec = searchItem.get("Description","") 

                if descriptionfromcode.translate(translation_table) == dec.translate(translation_table) and dec:
                    if code == 'D0120':
                        limitation = matching_dict.get("Exam")
                    elif code == 'D1110':
                        limitation = matching_dict.get("Prophy")     
                    elif code == 'D0274' :
                        limitation = matching_dict.get("Bitewing") 
                    elif code == 'D0210' or code == 'D0330':
                        limitation = matching_dict.get("Pano/FMXFrequency") 
                    elif code == 'D1351' :
                        limitation = matching_dict.get("MolarSealantFrequency") 
                    elif code == 'D2740' :
                        limitation =  matching_dict.get("Crown/prosthodonticsreplacementfrequency")       
                        

                    limitation = limitation 
                    Benefits =searchItem.get("PPO/Premier/OON","")
                    if '/' in Benefits:
                        Benefits = Benefits.split('/')[0].strip()

                    Agelimit =searchItem.get("AgeRange","")
                    waitperiod =searchItem.get("Waitingperiod","")
                    deductible = searchItem.get("DeductibleApplies","")
                    agelimit = str(limitation.strip(', ')+", "+ Agelimit.strip(', ')).replace(" N/A","")
                    
                    if 'NONE' in waitperiod:
                        waitperiod = ""
  
            
            EligibilityBenefits.append({
                "ProcedureCode": item.get("code").strip(),
                "ProcedureCodeDescription": item.get("search"),
                "Amount": "",
                "Type": "",
                "limitation": agelimit.strip(', '),
                "DeductibleApplies": deductible.strip(),
                "Copay": "",
                "Benefits": Benefits.strip(', '),
                "WaitingPeriod": waitperiod.strip(', ')
            })

            EligibilityServiceTreatmentHistory.append({
                "ProcedureCode": item.get("code").strip(),
                "LimitationText": limitation.strip(', '),
                "History": "",
                "Tooth": "",
                "Surface": "",
                "LimitationAlsoAppliesTo": "",
                "ProcedureCodeDescription": item.get("search")        
                })
            
            TreatmentHistorySummary.append({
                "ProcedureCode": item.get("code").strip(),
                "LimitationText": limitation.strip(', '),
                "History": "",
                "Tooth": "",
                "Surface": "",
                "LimitationAlsoAppliesTo": "",
                "ProcedureCodeDescription": item.get("search")           
                }) 
        
        if item.get("Proccode") == "D2391":
            EligibilityPatientVerification.update({"FamilyMemberWaitingPeriod":item.get("WaitingPeriod")})



    output={}

    output.update({"EligibilityPatientVerification":[EligibilityPatientVerification]})
    output.update({"EligibilityBenefits":EligibilityBenefits})
    output.update({"EligibilityMaximums":EligibilityMaximums})
    output.update({"EligibilityDeductiblesProcCode":EligibilityDeductiblesProcCode})
    output.update({"EligibilityServiceTreatmentHistory":EligibilityServiceTreatmentHistory})
    output.update({"TreatmentHistorySummary":TreatmentHistorySummary})
    output.update({"EligibilityAgeLimitation":[{"FamilyMember": "", "AgeLimit": ""}]})
    return output


# request=json.load(open(r"C:\BPK\Eligibility_Python\VSCODE\08_08\SD Payor Scraping\DelatdentalKansas.json", 'r'))
# data=json.load(open(r"C:\BPK\Eligibility_Python\VSCODE\08_08\SD Payor Scraping\output_.json", 'r'))
# output=main(data, request)
# with open("kansas_57742_.json", "w") as outfile:
#     json.dump(output, outfile, indent=4)
