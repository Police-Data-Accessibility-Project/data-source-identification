from enum import Enum

class AnnotationType(Enum):
    RELEVANCE = "RELEVANCE"
    RECORD_TYPE = "RECORD_TYPE"
    AGENCY = "AGENCY"


class BatchStatus(Enum):
    READY_TO_LABEL = "ready to label"
    IN_PROCESS = "in-process"
    ERROR = "error"
    ABORTED = "aborted"

class RecordType(Enum):
    """
    All available URL record types
    """
    ACCIDENT_REPORTS = "Accident Reports"
    ARREST_RECORDS = "Arrest Records"
    CALLS_FOR_SERVICE = "Calls for Service"
    CAR_GPS = "Car GPS"
    CITATIONS = "Citations"
    DISPATCH_LOGS = "Dispatch Logs"
    DISPATCH_RECORDINGS = "Dispatch Recordings"
    FIELD_CONTACTS = "Field Contacts"
    INCIDENT_REPORTS = "Incident Reports"
    MISC_POLICE_ACTIVITY = "Misc Police Activity"
    OFFICER_INVOLVED_SHOOTINGS = "Officer Involved Shootings"
    STOPS = "Stops"
    SURVEYS = "Surveys"
    USE_OF_FORCE_REPORTS = "Use of Force Reports"
    VEHICLE_PURSUITS = "Vehicle Pursuits"
    COMPLAINTS_AND_MISCONDUCT = "Complaints & Misconduct"
    DAILY_ACTIVITY_LOGS = "Daily Activity Logs"
    TRAINING_AND_HIRING_INFO = "Training & Hiring Info"
    PERSONNEL_RECORDS = "Personnel Records"
    ANNUAL_AND_MONTHLY_REPORTS = "Annual & Monthly Reports"
    BUDGETS_AND_FINANCES = "Budgets & Finances"
    CONTACT_INFO_AND_AGENCY_META = "Contact Info & Agency Meta"
    GEOGRAPHIC = "Geographic"
    LIST_OF_DATA_SOURCES = "List of Data Sources"
    POLICIES_AND_CONTRACTS = "Policies & Contracts"
    CRIME_MAPS_AND_REPORTS = "Crime Maps & Reports"
    CRIME_STATISTICS = "Crime Statistics"
    MEDIA_BULLETINS = "Media Bulletins"
    RECORDS_REQUEST_INFO = "Records Request Info"
    RESOURCES = "Resources"
    SEX_OFFENDER_REGISTRY = "Sex Offender Registry"
    WANTED_PERSONS = "Wanted Persons"
    BOOKING_REPORTS = "Booking Reports"
    COURT_CASES = "Court Cases"
    INCARCERATION_RECORDS = "Incarceration Records"
    OTHER = "Other"


class SuggestionType(Enum):
    """
    Identifies the specific kind of suggestion made for a URL
    """
    AUTO_SUGGESTION = "Auto Suggestion"
    USER_SUGGESTION = "User Suggestion"
    UNKNOWN = "Unknown"
    NEW_AGENCY = "New Agency"
    CONFIRMED = "Confirmed"

class SubmitResponseStatus(Enum):
    """
    Response statuses from the /source-collector/data-sources endpoint
    """
    SUCCESS = "success"
    FAILURE = "FAILURE"
    ALREADY_EXISTS = "already_exists"

class SuggestedStatus(Enum):
    """
    Possible values for user_relevant_suggestions:suggested_status
    """
    RELEVANT = "relevant"
    NOT_RELEVANT = "not relevant"
    INDIVIDUAL_RECORD = "individual record"
    BROKEN_PAGE_404 = "broken page/404 not found"