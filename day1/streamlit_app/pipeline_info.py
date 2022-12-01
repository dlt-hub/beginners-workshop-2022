import streamlit as st
import humanize

from dlt.pipeline.state import load_state_from_destination
from dlt.common import pendulum
from dlt.common.schema.typing import LOADS_TABLE_NAME, VERSION_TABLE_NAME

from _helpers import query_to_dataframe, pipeline

def write():
    """Display pipeline loading information. Will be moved to python-dlt once tested"""
    try:
        st.header("Pipeline info")
        st.markdown(f"""
        * pipeline name: **{pipeline.pipeline_name}**
        * destination: **{str(pipeline.sql_client().credentials)}** in **{pipeline.destination.__name__}**
        * dataset name: **{pipeline.dataset_name}**
        * default schema name: **{pipeline.default_schema_name}**
        """)

        st.header("Last load info")
        col1, col2, col3 = st.columns(3)
        loads_df = query_to_dataframe(f"SELECT load_id, inserted_at FROM {LOADS_TABLE_NAME} WHERE status = 0 ORDER BY inserted_at DESC LIMIT 101 ")
        loads_no = loads_df.shape[0]
        if loads_df.shape[0] > 0:
            rel_time = humanize.naturaldelta(pendulum.now() - loads_df.iloc[0, 1]) + " ago"
            last_load_id = loads_df.iloc[0, 0]
            if loads_no > 100:
                loads_no = "> " + str(loads_no)
        else:
            rel_time = "---"
            last_load_id = "---"
        col1.metric("Last load time", rel_time)
        col2.metric("Last load id", last_load_id)
        col3.metric("Total number of loads", loads_no)

        st.markdown("**Number of loaded rows:**")
        selected_load_id = st.selectbox("Select load id", loads_df)
        schema = pipeline.default_schema

        # construct a union query
        query_parts = []
        for table in schema.all_tables(with_dlt_tables=False):
            if "parent" in table:
                continue

            table_name = table["name"]
            query_parts.append(f"SELECT '{table_name}' as table_name, COUNT(1) As rows_count FROM {table_name} WHERE _dlt_load_id = '{selected_load_id}'")
            query_parts.append("UNION ALL")
        query_parts.pop()
        rows_counts_df = query_to_dataframe("\n".join(query_parts))

        st.markdown(f"Rows loaded in **{selected_load_id}**")
        st.dataframe(rows_counts_df)

        st.markdown("**Last 100 loads**")
        st.dataframe(loads_df)

        st.header("Schema updates")
        schemas_df = query_to_dataframe(f"SELECT schema_name, inserted_at, version, version_hash FROM {VERSION_TABLE_NAME} ORDER BY inserted_at DESC LIMIT 101 ")
        st.markdown("**100 recent schema updates**")
        st.dataframe(schemas_df)

        st.header("Pipeline state info")
        with pipeline.sql_client() as client:
            remote_state = load_state_from_destination(pipeline.pipeline_name, client)
        local_state = pipeline.state

        col1, col2 = st.columns(2)
        if remote_state:
            remote_state_version = remote_state["_state_version"]
        else:
            remote_state_version = "---"

        col1.metric("Local state version", local_state["_state_version"])
        col2.metric("Remote state version", remote_state_version)

        if remote_state_version != local_state["_state_version"]:
            st.warning("Looks like that local state is not yet synchronized or synchronization is disabled")

    except Exception as ex:
        st.error("Pipeline info could not be prepared. Did you load the data at least once?")
        st.exception(ex)
