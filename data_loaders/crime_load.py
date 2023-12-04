import io
import pandas as pd
import requests

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

RECORDS_AMOUNT = 2000
ORDER_BY = 'Date DESC'

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    url = 'https://data.cityofchicago.org/resource/xguy-4ndq.json'
    params = {
    '$limit': RECORDS_AMOUNT,
    '$order': ORDER_BY  # Replace 'timestamp_field' with the actual timestamp field name
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        json_data = response.json()
    else:
        raise Exception(f"Failed to retrieve data, status code: {response.status_code}")
      
    return pd.DataFrame(json_data)


@test
def test_output(output, *args) -> None:
    """
    Assert output is not None
    """
    assert output is not None, 'The output is undefined'

@test
def test_output_len(output, *args) -> None:
    """
    Check if output length is correct
    """
    assert len(output) == RECORDS_AMOUNT, 'The record amount returned is not correct'
