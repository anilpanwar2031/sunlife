"""
Eligibility Data Processor

This module provides functionalities to process scraped eligibility data from various sources. Given a JSON data structure
resulting from web scraping operations and the input request parameters used for scraping, the module performs several
transformations and computations to structure the data according to desired specifications.

Key functionalities:
- Extracting patient verification information.
- Parsing and structuring benefits and treatment history.
- Calculating various statistics based on the provided data.
- Formatting the data into a consistent and desired structure.

Input:
- Scrapped data in JSON format which contains raw data gathered from the web.
- Input request which provided context for the scraping operation.

Output:
- A dictionary structured with key details like patient verification, benefits, treatment history, etc.

Usage:
```python
from eligibility_data_processor import main_function_name  # Replace with actual main function name

# Sample input data
scraped_data = {...}  # Replace with your scraped data
input_request = {...}  # Replace with your input request data

# Process the data
processed_data = main(scraped_data, input_request)
"""

import json
import re
from typing import List, Dict, Union, Optional

from mapPDF import mapEligibilityPatientVerification


def changeNone(text):
    # if(text=="None" or text=="N/A" or text==None):
    #     return ""
    # else:
    #     return text

    return "" if text == "None" or text == "N/A" or text is None else text


def clean_and_convert_to_float(s: str) -> float:
    """Cleans the string and converts it to a float."""
    if not s or s.strip() == "N/A":
        return 0.0

    # Extract only digits, decimals, and negative signs using a regular expression
    cleaned_str = "".join(re.findall(r"[-\d.]", s))

    try:
        return float(cleaned_str)
    except ValueError:
        print(f"Failed to convert string '{s}' to float after cleaning.")
        return 0.0


def calculate_difference(value1: str, value2: str) -> str:
    """
    Calculate the difference between two string-formatted monetary values.

    The values can contain commas, dollar signs, or the text "N/A". The returned
    value will be in a formatted string representation with a dollar sign.

    Args:
    - value1 (str): The first monetary value in string format.
    - value2 (str): The second monetary value in string format.

    Returns:
    - str: The difference of the two values in formatted string representation, e.g., "$100.00".

    Example:
    calculate_difference("$150.00", "$50.00") -> "$100.00"
    calculate_difference("$150.00", "N/A") -> "$150.00"
    calculate_difference("N/A", "$50.00") -> "-$50.00"
    """
    value1_float = clean_and_convert_to_float(value1)
    value2_float = clean_and_convert_to_float(value2)

    difference = value1_float - value2_float
    return "0.00" if difference == 0.0 else f"${round(difference, 2):,.2f}"


def calculate_sum(value1: Union[str, None], value2: Union[str, None]) -> str:
    """
    Calculate the sum of two string-formatted numbers.

    Args:
    - value1 (Union[str, None]): The first string value. It can contain commas, dollar signs, or the text "N/A".
    - value2 (Union[str, None]): The second string value. It can also contain commas, dollar signs, or the text "N/A".

    Returns:
    - str: The sum of the two values in dollar format, e.g., $100.00.
    """
    value1 = (
        value1.replace(",", "").replace("N/A", "0").replace("$", "")
        if value1
        else "0.0"
    )
    value2 = (
        value2.replace(",", "").replace("N/A", "0").replace("$", "")
        if value2
        else "0.0"
    )

    return f"${float(value1) + float(value2):.2f}"


def merge_eligibility_benefits_data(
    data: List[Dict[str, Union[str, int]]]
) -> List[Dict[str, Union[str, int]]]:
    """
    Merge consecutive eligibility benefit data items if they can be combined.

    Args:
    - data (List[Dict[str, Union[str, int]]]): A list of dictionaries, where each dictionary represents an
                                               eligibility benefit item. Each dictionary may have keys like
                                               "Proccode", "ProcedureName", and "Procedure", among others.

    Returns:
    - List[Dict[str, Union[str, int]]]: A merged list of eligibility benefit items based on specific criteria.

    Note:
    This function assumes that if a dictionary doesn't have "ProcedureName" key, the next 1 or 2 dictionaries
    might have a matching "Proccode" that can be combined with the current dictionary.
    """

    merged_data = []
    i = 0

    while i < len(data):
        item = data[i]

        if "ProcedureName" not in item:
            base_item = item

            # Check the next two items
            for j in range(1, 3):
                if i + j < len(data):
                    next_item = data[i + j]
                    # Check if the next item has only "Proccode" and "ProcedureName"
                    # and the "Proccode" value is a substring of the "Procedure" key of base_item
                    if (
                        set(next_item.keys()) == {"Proccode", "ProcedureName"}
                        and next_item["Proccode"] in base_item["Procedure"]
                    ):
                        merged_item = {**base_item, **next_item}
                        merged_data.append(merged_item)
                        i += j  # Move the index to skip the items we've processed
                        break
            else:
                # If no match was found in the next two items, add the base_item to the result
                merged_data.append(base_item)
        else:
            # If the item already has "ProcedureName", add it to the result as is
            merged_data.append(item)

        i += 1

    return merged_data


def clean_key_value(data: Dict[str, str], key: str, prefix: str) -> str:
    """
    Cleans the value associated with a given key in the provided dictionary.

    Args:
    - key (str): The key to retrieve value from the dictionary.
    - prefix (str): The prefix to be removed from the retrieved value.

    Returns:
    - str: Cleaned value with the prefix, newline characters removed, and any leading or trailing whitespaces trimmed.
    """

    value = data.get(key, "")
    cleaned_value = re.sub(re.escape(prefix), "", value)  # replace the prefix
    cleaned_value = re.sub(
        r"\s*\n\s*", " ", cleaned_value
    )  # replace newlines and surrounding whitespace with a single space
    return cleaned_value.strip()


def update_eligibility_verification(
    verification: Dict[str, str], data: Dict[str, str], patient_data: Dict[str, str]
) -> Dict[str, str]:
    """
    Update the eligibility verification dictionary with data extracted from the given dictionaries.

    Args:
    - verification (Dict[str, str]): Initial dictionary with some eligibility verification details.
    - data (Dict[str, str]): Dictionary containing extracted data points.
    - patient_data (Dict[str, str]): Dictionary containing details about the patient.

    Returns:
    - Dict[str, str]: Updated eligibility verification dictionary with additional details.

    Example:
    verification = {}
    data = {
        "InsuranceCalendarOrFiscalPolicyYear": "Year: 2023.",
        "CoverageType": "COVERAGE TYPE: PPO",
        ...
    }
    patient_data = {
        "SubscriberId": "123456",
        "BirthDate": "01/01/2000",
        ...
    }
    updated_verification = update_eligibility_verification(verification, data, patient_data)
    """
    if data.get("InsuranceCalendarOrFiscalPolicyYear"):
        beniftyear = data.get("InsuranceCalendarOrFiscalPolicyYear").split(":")
        beniftyear = beniftyear[1].split(".")
        verification["InsuranceCalendarOrFiscalPolicyYear"] = beniftyear[0].strip()

    verification.update(
        {
            "FamilyMemberId": patient_data.get("SubscriberId"),
            "SubscriberId": patient_data.get("SubscriberId"),
            "SubscriberName": clean_key_value(
                data, "SubcriberName", "SUBSCRIBER NAME:"
            ),
            "ProgramType": clean_key_value(data, "CoverageType", "COVERAGE TYPE:"),
            "FamilyMemberDateOfBirth": patient_data.get("BirthDate"),
            "SubscriberDateOfBirth": patient_data.get("SubscriberBirthDate"),
            "GroupName": clean_key_value(data, "GroupName", "GROUP NAME:"),
            "GroupNumber": clean_key_value(data, "GroupNumber", "GROUP NUMBER:"),
            "ClaimPayerID": clean_key_value(
                data, "ElectronicPayerID", "ELECTRONIC CLAIMS PAYER ID:"
            ),
            "DependentChildCoveredAgeLimit": clean_key_value(
                data, "ChildCoverageAge", "Child Coverage Age:"
            ),
            "DependentStudentAgeLimit": clean_key_value(
                data, "StudentCoverageAge", "Student Coverage Age:"
            ),
            "OrthodonticAgeLimits": clean_key_value(
                data, "DependentOrthodonticAge", "Dependent Orthodontic Age:"
            ),
            "AdultOrthodonticCovered": clean_key_value(
                data, "AdultOrthodontic", "Adult Orthodontic:"
            ),
            "CoordinationofBenefits": "Yes",
            "CoordinationofBenefitsType": "Standard Coordination of Benefits",
            "oonBenefits": "Yes",
            "ClaimsAddress": data.get("mailingAddress", "").strip(),
            "ClaimMailingAddress": data.get("mailingAddress", "").strip(),
        }
    )

    return verification


def extract_waiting_period(
    eligibility_provisions: List[Dict], service_type: str = "PREVENTIVE"
) -> Optional[str]:
    """
    Extracts the waiting period duration for a specific service type.

    Args:
    - eligibility_provisions (List[Dict]): List of provision dictionaries.
    - service_type (str): The type of service to look for. Default is "PREVENTIVE".

    Returns:
    - str or None: The duration of the waiting period if found, otherwise None.
    """

    waiting_period = eligibility_provisions[1].get("WaitingPeriod", [])

    for item in waiting_period:
        if item.get("Services1") == service_type:
            return item.get("Duration1")
        elif item.get("Services2") == service_type:
            return item.get("Duration2")

    return None


def extract_provision_limitation(
    eligibility_provisions: List[Dict], service_keywords: List[str]
) -> Dict[str, str]:
    """
    Extracts provision details based on service keywords.

    Args:
    - eligibility_provisions (List[Dict]): List of provision dictionaries.
    - service_keywords (List[str]): Keywords to search for in the service items.

    Returns:
    - Dict[str, str]: A dictionary with provision details.
    """

    provisions_dict = {}
    provisions = eligibility_provisions[0].get("FrequencyAgeAndBenefitLimitations", [])

    for item in provisions:
        service = item.get("Services", "")
        frequency_and_limitation = item.get("FrequencyAndLimitation", "")

        if service_keywords[0] in service:  # Assuming "Resin" is the first keyword
            provisions_dict[
                "AlternativeBenefitProvision"
            ] = f"{service} , {frequency_and_limitation}"
        elif (
            service_keywords[1] in service
        ):  # Assuming "Missing Tooth Clause" is the second keyword
            provisions_dict["MissingToothClause"] = frequency_and_limitation
        elif (
            service_keywords[2] in service
        ):  # Assuming "Predetermination" is the third keyword
            provisions_dict["PreCertRequired"] = frequency_and_limitation
            provisions_dict["PreauthorizationRequired"] = frequency_and_limitation

    return provisions_dict


def update_family_member_info(
    item: Dict, patientdata: Dict, verification_dict: Dict
) -> None:
    """
    Update the verification dictionary with the family member's details.

    Args:
    - item (Dict): Dictionary containing the family member's information.
    - patientdata (Dict): Patient's data.
    - verification_dict (Dict): Dictionary to update.
    """

    Informaiton = str(item.get("Name", "")).split("Birthdate")
    name = Informaiton[0]
    birthdate, start, end = extract_dates(Informaiton)

    if str(patientdata.get("BirthDate")) == birthdate:
        updates = {
            "EligibilityStatus": "Active",
            "FamilyMemberName": name,
            "FamilyMemberEffectiveDate": start,
            "FamilyMemberEndDate": end,
            "IndividualAnnualDeductibleMet": item.get("RegANNDeductible", ""),
            "IndividualAnnualBenefitsUsedtoDate": item.get("RegANNMaximum", ""),
            "OrthodonticLifetimeBenefitUsedtoDate": item.get("OrthoLifeMaximum", ""),
        }
        verification_dict.update(updates)
    elif str(patientdata.get("SubscriberBirthDate")) == birthdate:
        updates = {"SubscriberEffectiveDate": start, "SubscriberEndDate": end}
        verification_dict.update(updates)


def extract_dates(information: List[str]) -> (str, str, str):
    """
    Extracts the birthdate, start, and end dates from the provided information.

    Args:
    - information (List[str]): List containing the details to extract dates from.

    Returns:
    - Tuple (birthdate, start, end)
    """

    birthdate_info = information[1].split("Start")
    birthdate = birthdate_info[0].strip()

    start_info = birthdate_info[1].split("End")
    start = start_info[0].strip()

    end = start_info[1]
    return birthdate, start, end


def update_family_deductible_ineligibility_verification(
    MaximumsDeductiblestUsed: List[Dict], patientdata: Dict, verification_dict: Dict
) -> None:
    """
    Update the EligibilityPatientVerification dictionary with Maximums & Deductibles data.

    Args:
    - MaximumsDeductiblestUsed (List[Dict]): List containing the Maximums & Deductibles data.
    - patientdata (Dict): Patient's data.
    - verification_dict (Dict): Dictionary to update.
    """

    for item in MaximumsDeductiblestUsed[1:]:
        if item.get("Name") != "FAMILY DEDUCTIBLES & MAXIMUMS":
            update_family_member_info(item, patientdata, verification_dict)
        elif item.get("Name") == "FAMILY DEDUCTIBLES & MAXIMUMS":
            updates = {
                "FamilyAnnualDeductibleMet": item.get("RegANNDeductible", ""),
                "FamilyAnnualBenefitsUsedtoDate": item.get("RegANNMaximum", ""),
            }
            verification_dict.update(updates)


def calculate_and_update_remaining_benefit(
    verification_dict: Dict, original_key: str, used_key: str, new_key: str
) -> None:
    original_value = verification_dict.get(original_key, "").strip()
    used_value = verification_dict.get(used_key, "").strip()

    if not original_value or not used_value:
        return

    remaining_value = calculate_difference(original_value, used_value)
    verification_dict[new_key] = remaining_value


def optimize_maximums_deductibles(
    MaximumsDeductiblesttotals: List[Dict], verification_dict: Dict
) -> None:
    """
    Update the verification dictionary with Maximums & Deductibles totals data.

    Args:
    - MaximumsDeductiblesttotals (List[Dict]): List containing the Maximums & Deductibles totals data.
    - verification_dict (Dict): Dictionary to update.
    """

    mappings = {
        "Annual Family Deductibles": "FamilyAnnualDeductible",
        "Ortho Lifetime Maximums": "OrthodonticLifetimeBenefit",
        "Annual Deductibles": "IndividualAnnualDeductible",
        "Annual Maximums": "IndividualAnnualMaximumBenefits",
    }

    for item in MaximumsDeductiblesttotals:
        key = mappings.get(item.get("Maximum/Deductible"))
        if key:
            verification_dict[key] = item.get("DeltaDentalPPO", "")

    benefit_calculations = [
        (
            "FamilyAnnualDeductible",
            "FamilyAnnualDeductibleMet",
            "FamilyAnnualDeductibleRemaining",
        ),
        (
            "IndividualAnnualDeductible",
            "IndividualAnnualDeductibleMet",
            "IndividualAnnualDeductibleRemaining",
        ),
        (
            "IndividualAnnualMaximumBenefits",
            "IndividualAnnualBenefitsUsedtoDate",
            "IndividualAnnualRemainingBenefit",
        ),
        (
            "OrthodonticLifetimeBenefit",
            "OrthodonticLifetimeBenefitUsedtoDate",
            "OrthodonticLifetimeRemainingBenefit",
        ),
    ]

    for original_key, used_key, new_key in benefit_calculations:
        calculate_and_update_remaining_benefit(
            verification_dict, original_key, used_key, new_key
        )


def append_to_eligibility_list(
    target_list: list,
    type_value: str,
    network: str,
    amount_key: str,
    remaining_key: str,
    service_category: str,
    family_individual: str,
    verification_dict: dict,
):
    """
    Appends a new entry to the target list using specified parameters and verification data.

    Args:
    - target_list (list): List to which the entry should be appended.
    - type_value (str): "Type" key value for the entry.
    - network (str): "Network" key value for the entry.
    - amount_key (str): Key to get amount from verification dict.
    - remaining_key (str): Key to get remaining amount from verification dict.
    - service_category (str): "ServiceCategory" key value for the entry.
    - family_individual (str): "Family_Individual" key value for the entry.
    - verification_dict (dict): Dictionary with verification data.

    Returns:
    None. The target_list is modified in-place.
    """
    entry = {
        "Type": type_value,
        "Network": network,
        "Amount": verification_dict.get(amount_key),
        "Remaining": verification_dict.get(remaining_key),
        "ServiceCategory": service_category,
        "Family_Individual": family_individual,
    }
    target_list.append(entry)


def update_eligibility_data(
    EligibilityMaximums: list,
    EligibilityDeductiblesProcCode: list,
    EligibilityPatientVerification: dict,
):
    """
    Updates the eligibility data lists based on the provided verification data.

    Args:
    - EligibilityMaximums (list): List to append max benefits data.
    - EligibilityDeductiblesProcCode (list): List to append deductible and procedure code data.
    - EligibilityPatientVerification (dict): Dictionary containing the verification data.

    Returns:
    None. Lists are modified in-place.
    """
    append_to_eligibility_list(
        EligibilityMaximums,
        "Annual Maximums",
        "PPO",
        "IndividualAnnualMaximumBenefits",
        "IndividualAnnualRemainingBenefit",
        "Dental",
        "Individual",
        EligibilityPatientVerification,
    )

    append_to_eligibility_list(
        EligibilityMaximums,
        "Orthodontic Lifetime",
        "PPO",
        "OrthodonticLifetimeBenefit",
        "OrthodonticLifetimeRemainingBenefit",
        "Orthodontics",
        "Individual",
        EligibilityPatientVerification,
    )

    append_to_eligibility_list(
        EligibilityDeductiblesProcCode,
        "Individual Annual Deductible",
        "PPO",
        "IndividualAnnualDeductible",
        "IndividualAnnualDeductibleRemaining",
        "Dental",
        "Individual",
        EligibilityPatientVerification,
    )

    append_to_eligibility_list(
        EligibilityDeductiblesProcCode,
        "Orthodontic Lifetime",
        "PPO",
        "FamilyAnnualDeductible",
        "FamilyAnnualDeductibleRemaining",
        "Dental",
        "Family",
        EligibilityPatientVerification,
    )


def extract_benefits_and_history_data(
    item: dict, EligibilityTreatmentHistory: list
) -> tuple:
    """
    Extracts benefits and history data from the provided item and history list.

    Args:
    - item (dict): Dictionary containing details about a procedure or treatment.
    - EligibilityTreatmentHistory (list): List containing treatment history data.

    Returns:
    tuple: Contains extracted values in the order of:
           - Procedure code description
           - Benefits associated with the procedure
           - Deductible status
           - History date of the procedure
           - Limitations or comments associated with the procedure
    """
    desc = str(item.get("ProcedureName", "")).split("-", 1)
    descpt = desc[1].strip() if len(desc) > 1 else ""

    benefit = item.get("DeltaDentalPPO", "") or "N/A"

    deduct = "N/A"
    comments = item.get("Comments")
    if comments:
        if "Deductible does not apply." in comments:
            deduct = "No"
        elif "Deductible Applies." in comments:
            deduct = "Yes"

    histroyDate, matched_procedure = match_history_date(
        descpt, EligibilityTreatmentHistory
    )
    limit = (
        comments.replace("Deductible does not apply.", "")
        .replace("Deductible Applies.", "")
        .strip()
        if comments
        else ""
    )

    return descpt, benefit, deduct, histroyDate, limit


def match_history_date(descpt: str, EligibilityTreatmentHistory: list) -> tuple:
    """
    Matches procedure description to historical data.

    Args:
    - descpt (str): Procedure description.
    - EligibilityTreatmentHistory (list): Historical data.

    Returns:
    tuple: Date of matched procedure and procedure. Default is ("N/A", None).
    """

    for history in EligibilityTreatmentHistory:
        procedure_lists = [
            history.get("procedure1", ""),
            history.get("procedure2", ""),
            history.get("procedure3", ""),
        ]
        for procedure in procedure_lists:
            if descpt in procedure or (
                re.search(r"s-\d", descpt) and descpt.split("s-")[0] in procedure
            ):
                return (
                    history.get(
                        f"DateOfService{str(procedure_lists.index(procedure) + 1)}",
                        "N/A",
                    ),
                    procedure,
                )

    return "N/A", None


def update_eligibility_data_lists(
    item: dict,
    descpt: str,
    benefit: str,
    deduct: str,
    histroyDate: str,
    limit: str,
    EligibilityBenefits: list,
    EligibilityServiceTreatmentHistory: list,
    TreatmentHistorySummary: list,
):
    """
    Updates eligibility data lists based on input item.

    Args:
    - item (dict): Data item with procedure details.
    - descpt (str): Procedure description.
    ...[other arguments]...
    - TreatmentHistorySummary (list): List to update treatment history.

    No return value; modifies input lists in-place.
    """
    common_data = {
        "ProcedureCode": "D" + item.get("Proccode", ""),
        "ProcedureCodeDescription": descpt,
    }

    EligibilityBenefits.append(
        {
            **common_data,
            "Amount": "",
            "Type": item.get("Type"),
            "limitation": limit,
            "DeductibleApplies": deduct,
            "Copay": "",
            "Benefits": benefit,
        }
    )

    for lst in [EligibilityServiceTreatmentHistory, TreatmentHistorySummary]:
        lst.append(
            {
                **common_data,
                "LimitationText": limit,
                "History": histroyDate,
                "Tooth": "",
                "Surface": "",
                "LimitationAlsoAppliesTo": "",
            }
        )


def process_item(
    item: dict,
    EligibilityTreatmentHistory: list,
    EligibilityBenefits: list,
    EligibilityServiceTreatmentHistory: list,
    TreatmentHistorySummary: list,
):
    """
    Processes a single eligibility item and updates relevant data lists.

    Args:
    - item (dict): Input data item for eligibility processing.
    - EligibilityTreatmentHistory (list): Treatment history data.
    ...[other arguments]...

    No return value; modifies input lists in-place.
    """
    descpt, benefit, deduct, histroyDate, limit = extract_benefits_and_history_data(
        item, EligibilityTreatmentHistory
    )
    update_eligibility_data_lists(
        item,
        descpt,
        benefit,
        deduct,
        histroyDate,
        limit,
        EligibilityBenefits,
        EligibilityServiceTreatmentHistory,
        TreatmentHistorySummary,
    )


def main(Scraperdata, request):
    """
    Orchestrates the processing of eligibility data using helper functions.

    This function extracts and processes patient verification, benefits, treatment history, and
    other related information by leveraging various helper functions.

    Returns:
    dict: A dictionary containing processed patient eligibility data structured as:
        - EligibilityPatientVerification (list): Verification data for the patient.
        - EligibilityBenefits (list): List of benefits associated with the patient.
        - EligibilityMaximums (list): Information on maximum benefits.
        - EligibilityDeductiblesProcCode (list): Deductible details with procedure codes.
        - EligibilityServiceTreatmentHistory (list): Treatment history with service details.
        - TreatmentHistorySummary (list): Summary of the patient's treatment history.
        - EligibilityAgeLimitation (list): Age limitations for different family members.
    """
    print("wrapper for wisconsin started")
    patientdata = request.get("PatientData")[0]
    EligibilityPatient = Scraperdata.get("EligibilityPatientVerification")[0]
    EligibilityMaximiums = Scraperdata.get("EligibilityMaximums")
    EligibilityBenefitsData = Scraperdata.get("EligibilityBenefits")
    EligibilityTreatmentHistory = Scraperdata.get("EligibilityServiceTreatmentHistory")
    EligibilityOtherProvisions = Scraperdata.get("EligibilityOtherProvisions")

    EligibilityPatientVerification = mapEligibilityPatientVerification()
    EligibilityMaximums = []
    EligibilityDeductiblesProcCode = []
    EligibilityServiceTreatmentHistory = []
    TreatmentHistorySummary = []
    EligibilityBenefits = []

    EligibilityPatientVerification.update(
        update_eligibility_verification(
            EligibilityPatientVerification, EligibilityPatient, patientdata
        )
    )

    family_waiting_duration = extract_waiting_period(EligibilityOtherProvisions)
    if family_waiting_duration:
        EligibilityPatientVerification.update(
            {"FamilyMemberWaitingPeriod": family_waiting_duration}
        )

    keywords = ["Resin", "Missing Tooth Clause", "Predetermination"]
    provision_limitations = extract_provision_limitation(
        EligibilityOtherProvisions, keywords
    )
    EligibilityPatientVerification.update(provision_limitations)

    MaximumsDeductiblestUsed = EligibilityMaximiums[0].get(
        "MaximumsDeductiblesAmountUsed"
    )

    update_family_deductible_ineligibility_verification(
        MaximumsDeductiblestUsed, patientdata, EligibilityPatientVerification
    )

    MaximumsDeductiblesttotals = EligibilityMaximiums[1].get(
        "MaximumsDeductiblesTotals"
    )

    optimize_maximums_deductibles(
        MaximumsDeductiblesttotals, EligibilityPatientVerification
    )

    update_eligibility_data(
        EligibilityMaximums,
        EligibilityDeductiblesProcCode,
        EligibilityPatientVerification,
    )

    EligibilityBenefitsData = merge_eligibility_benefits_data(EligibilityBenefitsData)

    for item in EligibilityBenefitsData:
        process_item(
            item,
            EligibilityTreatmentHistory,
            EligibilityBenefits,
            EligibilityServiceTreatmentHistory,
            TreatmentHistorySummary,
        )

    return {
        "EligibilityPatientVerification": [EligibilityPatientVerification],
        "EligibilityBenefits": EligibilityBenefits,
        "EligibilityMaximums": EligibilityMaximums,
        "EligibilityDeductiblesProcCode": EligibilityDeductiblesProcCode,
        "EligibilityServiceTreatmentHistory": EligibilityServiceTreatmentHistory,
        "TreatmentHistorySummary": TreatmentHistorySummary,
        "EligibilityAgeLimitation": [{"FamilyMember": "", "AgeLimit": ""}],
    }




