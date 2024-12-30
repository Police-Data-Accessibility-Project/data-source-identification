
def test_duplicates(api_test_helper):
    ath = api_test_helper

    config = {
            "example_field": "example_value",
            "sleep_time": 1
        }

    data = ath.request_validator.post(
        url="/collector/example",
        json=config
    )