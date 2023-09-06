from mapPDF import mapEligibilityPatientVerification
from datetime import datetime
import json
from re import search

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

def get_substring_between_strings(s, start, end):
    """
    Function to get a substring between two strings.
    Args:
        s (str): Input string
        start (str): Starting string
        end (str): Ending string

    Returns:
        str: Substring between start and end strings, or None if not found.
    """
    start_index = s.find(start)
    if start_index == -1:
        return None

    end_index = s.find(end, start_index + len(start))
    if end_index == -1:
        return None

    substring = s[start_index + len(start):end_index]
    return substring


def main(Scraperdata, request):
    patientdata = request.get("PatientData")[0]
    EligibilityPatient = Scraperdata.get("EligibilityPatientVerification")[0]
    EligibilityMaximiums = Scraperdata.get("EligibilityMaximums")
    EligibilityBenefitsData = Scraperdata.get("EligibilityBenefits")
    EligibilityTreatmentHistory = Scraperdata.get("EligibilityServiceTreatmentHistory")
    EligibilityOtherProvisions = Scraperdata.get("EligibilityOtherProvisions")

    EligibilityPatientVerification=mapEligibilityPatientVerification()
    EligibilityMaximums=[]
    EligibilityDeductiblesProcCode=[]
    EligibilityServiceTreatmentHistory=[]
    TreatmentHistorySummary=[]
    EligibilityBenefits=[]

    if EligibilityPatient.get("Coverageis") == "Active":
         EligibilityPatientVerification.update({"EligibilityStatus":"Active"})


    EligibilityPatientVerification.update({"FamilyMemberId":patientdata.get("SubscriberId")})
    EligibilityPatientVerification.update({"SubscriberId":patientdata.get("SubscriberId")})
    EligibilityPatientVerification.update({"SubscriberName":EligibilityPatient.get("Membername")})
    EligibilityPatientVerification.update({"ProgramType":EligibilityPatient.get("Coveragelevel")})
    EligibilityPatientVerification.update({"FamilyMemberName":patientdata.get("FirstName")+" "+patientdata.get("LastName")})
    EligibilityPatientVerification.update({"FamilyMemberDateOfBirth":patientdata.get("BirthDate")})
    EligibilityPatientVerification.update({"SubscriberDateOfBirth":patientdata.get("SubscriberBirthDate")})
    EligibilityPatientVerification.update({"FamilyMemberEffectiveDate":EligibilityPatient.get("Effectivedate")})
    EligibilityPatientVerification.update({"FamilyMemberEndDate":EligibilityPatient.get("Eligiblethrough")})
    EligibilityPatientVerification.update({"InsuranceFeeScheduleUsed":EligibilityPatient.get("Plantype")})
    EligibilityPatientVerification.update({"GroupName":EligibilityPatient.get("Groupname")})
    EligibilityPatientVerification.update({"GroupNumber":EligibilityPatient.get("Group")})    
    EligibilityPatientVerification.update({"DependentChildCoveredAgeLimit":EligibilityPatient.get("Dependenteligibility")})
    EligibilityPatientVerification.update({"DependentStudentAgeLimit":EligibilityPatient.get("Studenteligibility")})
    EligibilityPatientVerification.update({"InsuranceCalendarOrFiscalPolicyYear":EligibilityPatient.get("Benefitperiod")})
    EligibilityPatientVerification.update({"InNetworkOutNetwork":"In Network"})
    EligibilityPatientVerification.update({"oonBenefits":"Yes"})
    EligibilityPatientVerification.update({"CoordinationofBenefitsType":EligibilityPatient.get("COBcoveragetype")})
    EligibilityPatientVerification.update({"CoordinationofBenefits":"Yes"})

    if EligibilityOtherProvisions[0].get("ClaimAdress", None):
        EligibilityPatientVerification.update({"ClaimsAddress":EligibilityOtherProvisions[0].get("ClaimAdress").replace("\n\n","\n").replace("\n"," ").replace("Please mail all claims to:","")})
        EligibilityPatientVerification.update({"ClaimMailingAddress":EligibilityOtherProvisions[0].get("ClaimAdress").replace("\n\n","\n").replace("\n"," ").replace("Please mail all claims to:","")})
    else:
        EligibilityPatientVerification.update({"ClaimsAddress":"Delta Dental of New Jersey P.O. Box 16354 Little Rock, AR 72231"})
        EligibilityPatientVerification.update({"ClaimMailingAddress":"Delta Dental of New Jersey P.O. Box 16354 Little Rock, AR 72231"})
    
    all = EligibilityPatient.get("AlternativeBenefitProvision").split("Frequency:")
    altbenPro = all[0].split("\n")
    freq =  all[1].split("\n")
    limita = freq[0]
    EligibilityPatientVerification.update({"AlternativeBenefitProvision":str(altbenPro[0])+", "+str(limita)})
    EligibilityPatientVerification.update({"OrthodonticAgeLimits":EligibilityPatient.get("OrthodonticAgeLimit").replace("Age limit: ","")})
    EligibilityPatientVerification.update({"FamilyMemberWaitingPeriod":"N/A"})
    for toothclause in EligibilityBenefitsData:
        if toothclause.get("MissingToothClause", None):
            if toothclause.get("MissingToothClause") != "":
                mistothclause = toothclause.get("MissingToothClause").replace("Please note that the information displayed above may be more up to date than other sections of this page.","").replace("For diagnostic requirements, please refer to the required documentation chart below eligible benefits on this page.","")
                EligibilityPatientVerification.update({"MissingToothClause":mistothclause.replace("*","").strip()})
                break

    
    # EligibilityPatientVerification.update({"AdultOrthodonticCovered":EligibilityPatient.get("AdultOrthodontic").replace("Adult Orthodontic: ", "")})
    # EligibilityPatientVerification.update({"ClaimPayerID":EligibilityPatient.get("ElectronicPayerID").replace("ELECTRONIC CLAIMS PAYER ID: ", "")})
    # EligibilityPatientVerification.update({"ClaimMailingAddress":EligibilityPatient.get("ClaimMailingAddress").replace("Please mail claims and predeterminations to: ", "")})
    # EligibilityPatientVerification.update({"ClaimsAddress":EligibilityPatient.get("ClaimMailingAddress").replace("Please mail claims and predeterminations to: ", "")})
    # EligibilityPatientVerification.update({"FamilyMemberEffectiveDate":EligibilityPatient.get("Effective Date")})
    # EligibilityPatientVerification.update({"InsuranceFeeScheduleUsed":EligibilityPatient.get("Network Name")})
    # EligibilityPatientVerification.update({"MissingToothClause":"A missing tooth clause applies to services such as the initial placement of full or partial dentures, fixed bridges, implants, and implant crowns. These services are only covered if the natural teeth being replaced were extracted while covered under this plan"})
    # EligibilityPatientVerification.update({"DependentChildCoveredAgeLimit":"Dependent dental will be terminated when dependent has turned 26 years old"})
    # EligibilityPatientVerification.update({"CoordinationofBenefits":"Yes"})
    # EligibilityPatientVerification.update({"BenefitPeriod":EligibilityPatient.get("Benefit Period")})
    # EligibilityPatientVerification.update({"InNetworkOutNetwork":"The patient should see an In Network dentist for the best benefit, Lesser benefits are available by visiting a non-participating dentist"})
    # EligibilityPatientVerification.update({"oonBenefits":"Yes"})
    # EligibilityPatientVerification.update({"AlternativeBenefitProvision":"Composites are considered for posterior teeth which includes molars and pre-molars (bicuspids)"})
    # EligibilityPatientVerification.update({"OrthodonticAgeLimits":"if the bands/appliances were placed prior to age 19"})
    # EligibilityPatientVerification.update({"PreCertRequired":"No"})
    # EligibilityPatientVerification.update({"PreauthorizationRequired":"No"})
    # EligibilityPatientVerification.update({"CoordinationofBenefitsType":"Standard/Birthday Rule as defined by NAIC"})
    # EligibilityPatientVerification.update({"HowareBenefitsPaid":"The benefit for the initial fee is 25% of the lifetime maximum or the total fee, whichever is less"})
    # EligibilityPatientVerification.update({"TreatmentinProgressCoverage":"There are no benefits payable if the appliance or bands were placed prior to the effective date, unless treatment was in progress under prior group orthodontic coverage, and no lapse in coverage"})
    # EligibilityPatientVerification.update({"AutomaticPayments":"Yes"})
    # EligibilityPatientVerification.update({"ContinuationClaimNeeded":"No"})




    ####----Maximums and deductibles-----###
    MaximumsDeductibles = EligibilityMaximiums[0]
    try:
        lifetimeMax = MaximumsDeductibles.get("PlanMaximum").split("\n")
        lifetimeMax = lifetimeMax[0].replace("used","").replace("max","").strip().split("-")
        EligibilityPatientVerification.update({"FamilyLifetimeMaximumBenefits":lifetimeMax[1]})
        EligibilityPatientVerification.update({"FamilyLifetimeBenefitsUsedtoDate":lifetimeMax[0]})
        EligibilityPatientVerification.update({"FamilyLifetimeRemainingBenefit":calculate_difference(EligibilityPatientVerification.get("FamilyLifetimeMaximumBenefits").strip(),EligibilityPatientVerification.get("FamilyLifetimeBenefitsUsedtoDate").strip())})

        ortholifetimeMax = MaximumsDeductibles.get("OrthodonticMaximum").split("\n")
        ortholifetimeMax = ortholifetimeMax[0].replace("used","").replace("max","").strip().split("-")
        EligibilityPatientVerification.update({"OrthodonticLifetimeBenefit":ortholifetimeMax[1]})
        EligibilityPatientVerification.update({"OrthodonticLifetimeBenefitUsedtoDate":ortholifetimeMax[0]})
        EligibilityPatientVerification.update({"OrthodonticLifetimeRemainingBenefit":calculate_difference(EligibilityPatientVerification.get("OrthodonticLifetimeBenefit").strip(),EligibilityPatientVerification.get("OrthodonticLifetimeBenefitUsedtoDate").strip())})

        individualDeductibleAnnual = MaximumsDeductibles.get("Individualdeductible").split(",")
        EligibilityPatientVerification.update({"IndividualAnnualDeductible":individualDeductibleAnnual[0].replace("per year","").strip()})
        EligibilityPatientVerification.update({"IndividualAnnualDeductibleRemaining":individualDeductibleAnnual[1].replace("remains to be paid","").strip()})
        EligibilityPatientVerification.update({"IndividualAnnualDeductibleMet":calculate_difference(EligibilityPatientVerification.get("IndividualAnnualDeductible").strip(),EligibilityPatientVerification.get("IndividualAnnualDeductibleRemaining").strip())})

        familyDeductibleAnual = MaximumsDeductibles.get("Familydeductible").split(",")
        EligibilityPatientVerification.update({"FamilyAnnualDeductible":familyDeductibleAnual[0].replace("per year","").strip()})
        EligibilityPatientVerification.update({"FamilyAnnualDeductibleRemaining":familyDeductibleAnual[1].replace("remains to be paid","").strip()})
        EligibilityPatientVerification.update({"FamilyAnnualDeductibleMet":calculate_difference(EligibilityPatientVerification.get("FamilyAnnualDeductible").strip(),EligibilityPatientVerification.get("FamilyAnnualDeductibleRemaining").strip())})
    except:
        pass

            
    EligibilityMaximums.append({
        "Type": "Lifetime Maximum",
        "Network": "In Network",
        "Amount": EligibilityPatientVerification.get("FamilyLifetimeMaximumBenefits"),
        "Remaining": EligibilityPatientVerification.get("FamilyLifetimeRemainingBenefit"),
        "Used": EligibilityPatientVerification.get("FamilyLifetimeBenefitsUsedtoDate"),
        "ServiceCategory": "",
        "Family_Individual": "Family"
    })
    EligibilityMaximums.append({
        "Type": "Orthodontic Lifetime",
        "Network": "In Network",
        "Amount": EligibilityPatientVerification.get("OrthodonticLifetimeBenefit"),
        "Remaining": EligibilityPatientVerification.get("OrthodonticLifetimeRemainingBenefit"),
        "Used": EligibilityPatientVerification.get("OrthodonticLifetimeBenefitUsedtoDate"),
        "ServiceCategory": "Orthodontics",
        "Family_Individual": "Individual"
    })


    EligibilityDeductiblesProcCode.append({
        "Type": "Individual Annual Deductible",
        "Network": "In Network",
        "Amount": EligibilityPatientVerification.get("IndividualAnnualDeductible"),
        "Remaining": EligibilityPatientVerification.get("IndividualAnnualDeductibleRemaining"),
        "Used": EligibilityPatientVerification.get("IndividualAnnualDeductibleMet"),
        "ServiceCategory": "",
        "Family_Individual": "Individual"
    })
    EligibilityDeductiblesProcCode.append({
        "Type": "Family Annual Deductible",
        "Network": "In Network",
        "Amount": EligibilityPatientVerification.get("FamilyAnnualDeductible"),
        "Remaining": EligibilityPatientVerification.get("FamilyAnnualDeductibleRemaining"),
        "Used": EligibilityPatientVerification.get("FamilyAnnualDeductibleMet"),
        "ServiceCategory": "",
        "Family_Individual": "Family"
    })

    ##----Procedures Codes----###
    for items in EligibilityBenefitsData:
        if items.get("Procedurecode") == "":
            continue

        data = items.get("ProcedureName").split("\n")
        procedurecode = items.get("Proccode")
        procedurename = data[0]
        procedurDescription = data[1]
        toothType = data[2].replace("Tooth Type ","")

        limiation =""
        if items.get("Covered") != "":
            dataCoverd = items.get("Covered").split("\n")
            status = dataCoverd[0]
            benefit = dataCoverd[1].replace("Plan Pays ","")
            deductible = dataCoverd[2].strip()
            if deductible == "No Deductible":
                deductible = "No"
            elif deductible == "Deductible":
                deductible = "Yes"
            else:
                deductible = ""
            try:
                limiation = dataCoverd[3]
            except:
                pass

        # if search("Waiting Period remaining:", items.get("Variations")) and items.get("Variations") != "Variations\nN/A":
        #     dataVaritation = items.get("Variations").split("Age limitations:")
        #     dataVaritation = dataVaritation[1].split("\n")
        #     ageLimitation = dataVaritation[0]
        #     dataVaritation = dataVaritation[1].split("Waiting Period remaining:")
        #     dataVaritation = dataVaritation[1].split("\n")
        #     waitingPeriod = dataVaritation[0]
        
        ageLimitation = get_substring_between_strings(items.get("Variations"), "Age limitations:", "\n")
        if ageLimitation == None:
            ageLimitation = " "
        
        waitingPeriod = get_substring_between_strings(items.get("Variations"), "Waiting Period remaining:", "\n")
        if waitingPeriod == None:
            waitingPeriod = " "

        treatmentHistory = items.get("TreatmentHistory").replace("Treatment History\n","")
        if treatmentHistory !="N/A":
            treatmentHistory = treatmentHistory.replace("\n",", ")
            if search("Related", treatmentHistory):
                treatmentHistory = treatmentHistory.split("Related")
                treatmentHistory = treatmentHistory[0].strip()

        treatmentHistory = treatmentHistory.rstrip(',').replace(" - -","")

        EligibilityBenefits.append({
            "ProcedureCode": "D"+procedurecode,
            "ProcedureCodeDescription": procedurDescription,
            "Amount": "",
            "Type": procedurename,
            "limitation": limiation+" "+ ageLimitation.strip(),
            "DeductibleApplies": deductible,
            "Copay": "",
            "Benefits": benefit,
            "WaitingPeriod": waitingPeriod.replace("-","").strip()
        })

        EligibilityServiceTreatmentHistory.append({
            "ProcedureCode": "D"+procedurecode,
            "LimitationText": limiation+" "+ ageLimitation.strip(),
            "History": treatmentHistory,
            "Tooth": toothType,
            "Surface": "",
            "LimitationAlsoAppliesTo": "",
            "ProcedureCodeDescription": procedurDescription
        })


        TreatmentHistorySummary.append({
            "ProcedureCode": "D"+procedurecode,
            "LimitationText": limiation+" "+ ageLimitation.strip(),
            "History": treatmentHistory,
            "Tooth": toothType,
            "Surface": "",
            "LimitationAlsoAppliesTo": "",
            "ProcedureCodeDescription": procedurDescription
        })
                    
    ###Only for EligibilityotherProvisions and claim ID###
    eligibilityOtherProvisions = ""
    for val in EligibilityBenefits:
        if val.get("ProcedureCodeDescription") == "Procedure code is not covered under plan.":
            continue
        if val.get("ProcedureCode") == "D2391":
            eligibilityOtherProvisions = val.get("ProcedureCodeDescription")+", "+val.get("limitation")
        if val.get("ProcedureCode") == "D2392":
            eligibilityOtherProvisions =eligibilityOtherProvisions +" "+ val.get("ProcedureCodeDescription")+", "+val.get("limitation")

        EligibilityPatientVerification.update({"AlternativeBenefitProvision":eligibilityOtherProvisions})

    ###Only for EligibilityotherProvisions and claim ID###  

    # EligibilityPatientVerification.update({"FamilyMemberId":temp.get("Member ID").replace("Member ID: ", "")})
    # EligibilityPatientVerification.update({"GroupNumber":temp.get("Insurance Group Number")})
    # EligibilityPatientVerification.update({"FamilyMemberEndDate":temp.get("Insurance End Period")})

    # date_str = temp.get("Insurance End Period")
    # date_format = "%m/%d/%Y"
    # target_date = datetime.strptime(date_str, date_format).date()
    # current_date = datetime.now().date()
    # if target_date > current_date:
    #     EligibilityPatientVerification.update({"EligibilityStatus":"Active"})

    # EligibilityPatientVerification.update({"PlanType":temp.get("Insurance Group Name")})
    # EligibilityPatientVerification.update({"IndividualAnnualMaximumBenefits":temp.get("Insurance Calendar or Fiscal Policy Year").replace("Calendar Year Max: ", "")})
    # EligibilityPatientVerification.update({"InsuranceFeeScheduleUsed":temp.get("Insurance Group Name")})
    # EligibilityPatientVerification.update({"FamilyMemberEffectiveDate":temp.get("Insurance Effective Date")})
    # EligibilityPatientVerification.update({"ClaimMailingAddress":"GEHA PO Box 21542 Eagan, MN 55121"})
    # EligibilityPatientVerification.update({"ClaimsAddress":"GEHA PO Box 21542 Eagan, MN 55121"})

    # EligibilityPatientVerification.update({"IndividualAnnualMaximumBenefits":plan.get("Calendar year maximum").get("InNetwork").replace(" per person", "")})
    
    # EligibilityPatientVerification.update({"IndividualLifetimeMaximumBenefits":plan.get("Orthodontic").get("InNetworkLifetimeMaximum").replace(" per person", "")})
    # EligibilityPatientVerification.update({"OrthodonticLifetimeBenefit":plan.get("Orthodontic").get("InNetworkLifetimeMaximum").replace(" per person", "")})
    
    

    output={}
    
    output.update({"EligibilityPatientVerification":[EligibilityPatientVerification]})
    output.update({"EligibilityBenefits":EligibilityBenefits})
    output.update({"EligibilityMaximums":EligibilityMaximums})
    output.update({"EligibilityDeductiblesProcCode":EligibilityDeductiblesProcCode})
    output.update({"EligibilityServiceTreatmentHistory":EligibilityServiceTreatmentHistory})
    output.update({"TreatmentHistorySummary":TreatmentHistorySummary})
    output.update({"EligibilityAgeLimitation":[{"FamilyMember": "", "AgeLimit": ""}]})
    return output

# request=json.load(open(r"C:\Users\iamha\Desktop\BPK teck\All Payors\SDB EXTERNAL\Conecticut\SD%20Payor%20Scraping\conecticut.json", 'r'))
# data=json.load(open(r"C:\Users\iamha\Desktop\BPK teck\All Payors\SDB EXTERNAL\Conecticut\SD%20Payor%20Scraping\output.json", 'r'))
# output=main(data, request)
# with open("ConnecticutOutput-RyanWest.json", "w") as outfile:
#     json.dump(output, outfile, indent=4)
