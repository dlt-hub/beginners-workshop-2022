import _env
import streamlit as st
import pandas as pd

import dlt
from dlt.helpers.pandas import query_results_to_df

# attach to existing pipeline
pipeline = dlt.attach(pipeline_name="chess")


# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def query_to_dataframe(query: str) -> pd.DataFrame:
    # dlt pipeline exposes configured sql client that (among others) let's you make queries against the warehouse
    with pipeline.sql_client() as client:
        df = query_results_to_df(client, query)
        return df


def run_sql(sql):
    with pipeline.sql_client() as client:
        return client.execute_sql(sql)


def to_fully_qualified_name(name):
    return pipeline.sql_client().make_qualified_table_name(name)