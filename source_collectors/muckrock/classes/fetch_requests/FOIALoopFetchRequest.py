from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest


class FOIALoopFetchRequest(FetchRequest):
    jurisdiction: int
