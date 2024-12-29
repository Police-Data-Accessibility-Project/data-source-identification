
def test_read_main(api_test_helper):

    data = api_test_helper.request_validator.get(url="/?test=test")
    assert data == {"message": "Hello World"}