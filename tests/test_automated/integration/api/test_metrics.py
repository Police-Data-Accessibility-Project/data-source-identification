import pytest


@pytest.mark.asyncio
async def test_get_batches_aggregated_metrics(api_test_helper):
    # Create successful batches with URLs of different statuses

    # Create failed batches

    raise NotImplementedError

@pytest.mark.asyncio
async def test_get_batches_breakdown_metrics(api_test_helper):
    raise NotImplementedError

@pytest.mark.asyncio
async def test_get_urls_breakdown_submitted_metrics(api_test_helper):
    # Create URLs with submitted status, broken down in different amounts by different weeks
    # And ensure the URLs are

@pytest.mark.asyncio
async def test_get_urls_breakdown_pending_metrics(api_test_helper):
    # Build URLs, broken down into three separate weeks,
    # with each week having a different number of pending URLs
    # with a different number of kinds of annotations per URLs

    # Additionally, add some URLs that are submitted,
    # validated, errored, and ensure they are not counted


    raise NotImplementedError

@pytest.mark.asyncio
async def test_get_backlog_metrics(api_test_helper):
    # Populate the backlog table and test that backlog metrics returned on a weekly basis

    # Ensure that multiple days in each week are added to the backlog table, with different values

    # Test that the count closest to the beginning of the week is returned for each week

    raise NotImplementedError
