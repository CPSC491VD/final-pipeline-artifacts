import pandas as pd
import pytz
from pandas import DataFrame
from datetime import datetime


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def clean_column(column_name):
    return column_name.lower().replace(' ', '_')

def convert_utc_to_pst(fmt: str):
    """Convert UTC date to PST date"""
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific'))
    pst_date = date.strftime(fmt)
    return pst_date


@transformer
def chicago_data_transform(df: DataFrame, *args, **kwargs) -> DataFrame:
    """
    Execute Transformer Action: ActionType.NORMALIZE

    Docs: https://docs.mage.ai/guides/transformer-blocks#normalize-data
    
    """

    df.columns = [clean_column(col) for col in df.columns]

    df = df.rename(columns={'date': 'crime_date', 'year': 'year_of'})
    df = df.drop(columns=['location', 'x_coordinate', 'y_coordinate'], axis=1)

    df['crime_date'] = pd.to_datetime(df['crime_date'])
    print(df['crime_date'])
    df['updated_on'] = pd.to_datetime(df['updated_on'])

    cols = list(df.columns.values)
    cols.pop(cols.index('latitude'))
    cols.pop(cols.index('longitude'))
    df = df[cols+['latitude','longitude']]


    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)

    # Format PST date
    fmt = '%Y %m-%d %H'
    pst_date = convert_utc_to_pst(fmt=fmt)
    df['insert_date'] = pst_date

    # Datetime dimension table
    datetime_dim = df[['crime_date']].drop_duplicates().reset_index(drop=True)
    datetime_dim['day'] = datetime_dim['crime_date'].dt.day
    datetime_dim['month'] = datetime_dim['crime_date'].dt.month
    datetime_dim['year'] = datetime_dim['crime_date'].dt.year
    datetime_dim['hour'] = datetime_dim['crime_date'].dt.hour
    datetime_dim['datetime_id'] = datetime_dim.index
    datetime_dim = datetime_dim[['datetime_id', 'month', 'day', 'year', 'hour', 'crime_date']]

    # Location dim table
    location_dim = df[['latitude', 'longitude', 'location_description', 'block']].drop_duplicates().reset_index(drop=True)
    location_dim['location_id'] = location_dim.index
    location_dim = location_dim[['location_id', 'latitude', 'longitude', 'location_description', 'block']]

    # Fact table
    fact_table = df.merge(datetime_dim, on=['crime_date']) \
                .merge(location_dim, on=['latitude', 'longitude', 'location_description', 'block']) \
            [['id', 'datetime_id', 'description', 'location_id', 'community_area', 'iucr', 'case_number', 'domestic', 'primary_type', 'arrest', 'fbi_code']]
    fact_table['iucr'] = fact_table['iucr'].str.lstrip('0')
    return {
        "crime_fact_table": fact_table.to_dict(orient="dict"),
        "crime_date_dimension": datetime_dim.to_dict(orient="dict"),
        "crime_location_dimension": location_dim.to_dict(orient="dict")
    }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

