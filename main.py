import requests

import xml.etree.ElementTree as ET
import pandas as pd
#from gspread_dataframe import set_with_dataframe
import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

PAISES = ['AUS', 'CHL', 'MDG', 'MHL', 'NLD', 'PER']

KPIS = {"muerte": ["Number of deaths", "Number of infant deaths", "Number of under-five deaths",
                   "Mortality rate for 5-14 year-olds (probability of dying per 1000 children aged 5-14 years)",
                   "Adult mortality rate (probability of dying between 15 and 60 years per 1000 population)",
                   "Estimates of number of homicides",
                   "Crude suicide rates (per 100 000 population)",
                   "Mortality rate attributed to unintentional poisoning (per 100 000 population)",
                   "Number of deaths attributed to non-communicable diseases, by type of disease and sex",
                   "Estimated road traffic death rate (per 100 000 population)",
                   "Estimated number of road traffic deaths"] ,
        "peso": ["Mean BMI (crude estimate)",
                 "Mean BMI (age-standardized estimate)",
                 "Prevalence of obesity among adults, BMI > 30 (age-standardized estimate) (%)",
                 "Prevalence of obesity among children and adolescents, BMI > +2 standard deviations above the median (crude estimate) (%)",
                 "Prevalence of overweight among adults, BMI > 25 (age-standardized estimate) (%)",
                 "Prevalence of overweight among children and adolescents, BMI > +1 standard deviations above the median (crude estimate) (%)",
                 "Prevalence of underweight among adults, BMI < 18.5 (age-standardized estimate) (%)",
                 "Prevalence of thinness among children and adolescents, BMI < -2 standard deviations below the median (crude estimate) (%)"
                 ],
        "salud": ["Alcohol, recorded per capita (15+) consumption (in litres of pure alcohol)",
                  "Estimate of daily cigarette smoking prevalence (%)",
                  "Estimate of daily tobacco smoking prevalence (%)",
                  "Estimate of current cigarette smoking prevalence (%)",
                  "Estimate of current tobacco smoking prevalence (%)",
                  "Mean systolic blood pressure (crude estimate)",
                  "Mean fasting blood glucose (mmol/l) (crude estimate)",
                  "Mean Total Cholesterol (crude estimate)" ] }

INCLUDE = [ "GHO", "COUNTRY", "SEX", "YEAR", "GHECAUSES", "AGEGROUP", "Display", "Numeric", "Low", "High"]




def checked(kpi):
    for element in KPIS["muerte"]:
        if element == kpi:
            return True
    for element in KPIS["peso"]:
        if element == kpi:
            return True
    for element in KPIS["salud"]:
        if element == kpi: 
            return True

    return False

def extract(fact, kpi):
    validated = checked(kpi)
    answer = []
    if validated:
        for needed in INCLUDE:
            new = fact.find(needed)
            if new is not None:
                if needed ==  "Numeric" or needed ==  "Low" or needed == "High":
                    answer.append(float(new.text))
                else:
                    answer.append(new.text)
            else:
                answer.append(None)

        return answer

    else:
        return False





values = []
values.append(INCLUDE)
for pais in PAISES:
    url = f"http://tarea-4.2021-1.tallerdeintegracion.cl/gho_{pais}.xml"
    response = requests.get(url)
    xml_info = response.content
    Arbol = ET.fromstring(xml_info)


    counter = 0
    for Fact in Arbol:
        print(f"imprimiendo fact: {counter}")

        info = Fact.find("GHO")
        row = extract(Fact, info.text)
        if row:
            values.append(row)
        counter +=1



print("listo")
print(values)
largo_filas = len(values)

#ACCES GOOGLE SHEET

secret_key = 'client_secret.json'

scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
secret_file = os.path.join(os.getcwd(), secret_key)


spreadsheet_id = '1POPShbZxXZDivEXDF8iZvq3j2G6xTcqoxHRdtEomq_A'
range_name = f'datos!A1:J{largo_filas}'

credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
service = discovery.build('sheets', 'v4', credentials=credentials)

data = { 'values': values}

service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data, range=range_name, valueInputOption='USER_ENTERED').execute()

















