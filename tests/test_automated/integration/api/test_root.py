def test_read_main(api_test_helper):

    data = api_test_helper.request_validator.get(url="/?test=test")
    assert data == {"message": "Hello World"}


def test_root_endpoint_with_mocked_dependency(client):
    response = client.get(
        url="/",
        params={"test": "test"},
        headers={"Authorization": "Bearer token"}
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Hello World"}, response.text



