import pytest

from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO, ManualBatchInnerInputDTO
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.external.url_request.core import URLRequestInterface


@pytest.mark.asyncio
@pytest.mark.manual
async def test_url_html_task_operator(
    adb_client_test,
):
    urls_to_insert = [
        "https://www.albanyca.org/departments/fire-department/programs-classes-events",
        "https://www.albanyca.gov/Departments/Police-Department/Crime-Mapping",
        "https://www.facebook.com/AlbanyPoliceCa/",
        "https://www.governmentjobs.com/careers/albanyca/jobs/3395149/police-officer?pagetype=jobOpportunitiesJobs",
        "https://www.albanyca.org/",
        "https://www.albanyca.gov/Departments/Police-Department",
        "https://www.joinalbanypd.us/",
        "https://www.albanyca.gov/Departments/Police-Department/Contact-Albany-Police",
        "https://www.albanyca.org/departments/police-department/policies-procedures-training-sb978",
        "https://www.yelp.com/biz/albany-police-department-albany-3",
    ]
    parser = HTMLResponseParser()
    manual_batch_dto = ManualBatchInputDTO(
        name="Test Batch",
        entries=[
            ManualBatchInnerInputDTO(url=url) for url in urls_to_insert
        ]
    )
    await adb_client_test.upload_manual_batch(dto=manual_batch_dto, user_id=1)
    operator = URLHTMLTaskOperator(
        adb_client=adb_client_test,
        url_request_interface=URLRequestInterface(),
        html_parser=parser
    )
    run_info = await operator.run_task(1)
    pass