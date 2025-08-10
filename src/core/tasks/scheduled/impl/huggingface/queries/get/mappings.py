from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse

FINE_COARSE_RECORD_TYPE_MAPPING = {
    # Police and Public
    RecordType.ACCIDENT_REPORTS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.ARREST_RECORDS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.CALLS_FOR_SERVICE: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.CAR_GPS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.CITATIONS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.DISPATCH_LOGS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.DISPATCH_RECORDINGS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.FIELD_CONTACTS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.INCIDENT_REPORTS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.MISC_POLICE_ACTIVITY: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.OFFICER_INVOLVED_SHOOTINGS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.STOPS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.SURVEYS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.USE_OF_FORCE_REPORTS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    RecordType.VEHICLE_PURSUITS: RecordTypeCoarse.POLICE_AND_PUBLIC,
    # Info About Officers
    RecordType.COMPLAINTS_AND_MISCONDUCT: RecordTypeCoarse.INFO_ABOUT_OFFICERS,
    RecordType.DAILY_ACTIVITY_LOGS: RecordTypeCoarse.INFO_ABOUT_OFFICERS,
    RecordType.TRAINING_AND_HIRING_INFO: RecordTypeCoarse.INFO_ABOUT_OFFICERS,
    RecordType.PERSONNEL_RECORDS: RecordTypeCoarse.INFO_ABOUT_OFFICERS,
    # Info About Agencies
    RecordType.ANNUAL_AND_MONTHLY_REPORTS: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    RecordType.BUDGETS_AND_FINANCES: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    RecordType.CONTACT_INFO_AND_AGENCY_META: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    RecordType.GEOGRAPHIC: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    RecordType.LIST_OF_DATA_SOURCES: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    RecordType.POLICIES_AND_CONTRACTS: RecordTypeCoarse.INFO_ABOUT_AGENCIES,
    # Agency-Published Resources
    RecordType.CRIME_MAPS_AND_REPORTS: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.CRIME_STATISTICS: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.MEDIA_BULLETINS: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.RECORDS_REQUEST_INFO: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.RESOURCES: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.SEX_OFFENDER_REGISTRY: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    RecordType.WANTED_PERSONS: RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
    # Jails and Courts Specific
    RecordType.BOOKING_REPORTS: RecordTypeCoarse.JAILS_AND_COURTS,
    RecordType.COURT_CASES: RecordTypeCoarse.JAILS_AND_COURTS,
    RecordType.INCARCERATION_RECORDS: RecordTypeCoarse.JAILS_AND_COURTS,
    # Other
    None: RecordTypeCoarse.NOT_RELEVANT
}

OUTCOME_RELEVANCY_MAPPING = {
    URLStatus.SUBMITTED: True,
    URLStatus.VALIDATED: True,
    URLStatus.NOT_RELEVANT: False
}