from enum import Enum


class RecordTypeCoarse(Enum):
    INFO_ABOUT_AGENCIES = "Info About Agencies"
    INFO_ABOUT_OFFICERS = "Info About Officers"
    AGENCY_PUBLISHED_RESOURCES = "Agency-Published Resources"
    POLICE_AND_PUBLIC = "Police & Public Interactions"
    POOR_DATA_SOURCE = "Poor Data Source"
    NOT_RELEVANT = "Not Relevant"
    JAILS_AND_COURTS = "Jails & Courts Specific"
    OTHER = "Other"