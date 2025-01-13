from helpers.DBDataCreator import DBDataCreator


def test_process_relevancy(api_test_helper):
    dbc: DBDataCreator = api_test_helper.db_data_creator

    # Create batch with status `in-process` and strategy `example`
    batch_id = dbc.batch()
    # Create 2 URLs with outcome `pending`
    dbc.urls(batch_id=batch_id, url_count=2)
    # Call `/process/relevancy`
    response = api_test_helper.request_validator.process_relevancy()

    # Wait for process to finish

    # Check URL metadata

    # URL metadata should show that one has
    # a `Relevant` attribute with value `true`
    # the other a `Relevant` attribute with value `false`
    # and both should have
    # a `validation_status` of `Pending Label Studio`
    # and a `validation_source` of `Machine Learning`

    # Huggingface Interface should have been called with batch of both urls

    # Label Studio should have been called with batch of both urls