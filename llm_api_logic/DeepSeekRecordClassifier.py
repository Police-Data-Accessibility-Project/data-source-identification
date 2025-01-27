import os

from openai import OpenAI

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from core.enums import RecordType

QUERY_CONTENT = """
    You will be provided with structured data from a web page and determine 
    the record type.
    
    The record types are as follows

    "Accident Reports": Records of vehicle accidents.
    "Arrest Records": Records of each arrest made in the agency's jurisdiction.
    "Calls for Service": Records of officers initiating activity or responding to requests for police response. Often called "Dispatch Logs" or "Incident Reports" when published.
    "Car GPS": Records of police car location. Not generally posted online.
    "Citations": Records of low-level criminal offenses where a police officer issued a citation instead of an arrest.
    "Dispatch Logs": Records of calls or orders made by police dispatchers.
    "Dispatch Recordings": Audio feeds and/or archives of municipal dispatch channels.
    "Field Contacts": Reports of contact between police and civilians. May include uses of force, incidents, arrests, or contacts where nothing notable happened.
    "Incident Reports": Reports made by police officers after responding to a call which may or may not be criminal in nature. Not generally posted online.
    "Misc Police Activity": Records or descriptions of police activity not covered by other record types.
    "Officer Involved Shootings": Case files of gun violence where a police officer was involved, typically as the shooter. Detailed, often containing references to records like Media Bulletins and Use of Force Reports.
    "Stops": Records of pedestrian or traffic stops made by police.
    "Surveys": Information captured from a sample of some population, like incarcerated people or magistrate judges. Often generated independently.
    "Use of Force Reports": Records of use of force against civilians by police officers.
    "Vehicle Pursuits": Records of cases where police pursued a person fleeing in a vehicle.
    "Complaints & Misconduct": Records, statistics, or summaries of complaints and misconduct investigations into law enforcement officers.
    "Daily Activity Logs": Officer-created reports or time sheets of what happened on a shift. Not generally posted online.
    "Training & Hiring Info": Records and descriptions of additional training for police officers.
    "Personnel Records": Records of hiring and firing, certification, discipline, and other officer-specific events. Not generally posted online.
    "Annual & Monthly Reports": Often in PDF form, featuring summaries or high-level updates about the police force. Can contain versions of other record types, especially summaries.
    "Budgets & Finances": Budgets, finances, grants, or other financial documents.
    "Contact Info & Agency Meta": Information about organizational structure, including department structure and contact info.
    "Geographic": Maps or geographic data about how land is divided up into municipal sectors, zones, and jurisdictions.
    "List of Data Sources": Places on the internet, often data portal homepages, where many links to potential data sources can be found.
    "Policies & Contracts": Policies or contracts related to agency procedure.
    "Crime Maps & Reports": Records of individual crimes in map or table form for a given jurisdiction.
    "Crime Statistics": Summarized information about crime in a given jurisdiction.
    "Media Bulletins": Press releases, blotters, or blogs intended to broadly communicate alerts, requests, or other timely information.
    "Records Request Info": Portals, forms, policies, or other resources for making public records requests.
    "Resources": Agency-provided information or guidance about services, prices, best practices, etc.
    "Sex Offender Registry": Index of people registered, usually by law, with the government as sex offenders.
    "Wanted Persons": Names, descriptions, images, and associated information about people with outstanding arrest warrants.
    "Booking Reports": Records of booking or intake into corrections institutions.
    "Court Cases": Records such as dockets about individual court cases.
    "Incarceration Records": Records of current inmates, often with full names and features for notification upon inmate release.
    "Other": Other record types not otherwise described.

    Output the record type in the following format. Do not include any other information:

    {
        "record_type": "<record_type>"
    }    
    """

def dictify_html_info(html_info: URLHTMLContentInfo) -> dict:



class DeepSeekRecordClassifier:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def build_query_messages(self, html_info: URLHTMLContentInfo) -> list[dict[str, str]]:
        insert_content = dictify_html_info(html_info)
        return [
            {
                "role": "system",
                "content": QUERY_CONTENT
            },
            {
                "role": "user",
                "content": f"```json{insert_content}```"
            }
        ]

    def classify_url(self, url_with_html: URLWithHTML) -> RecordType:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.build_query_messages(url_with_html.html_infos[0]),
            stream=False,
            response_format={
                'type': 'json_object'
            }
        )
