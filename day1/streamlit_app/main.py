import streamlit as st

import sql_queries
import data_explorer
import using_sql_views
import pipeline_info

PAGES = {
    "Pipeline info": pipeline_info, 
    "Explore data": data_explorer,
    "SQL queries": sql_queries,
    "Using SQL Joins": using_sql_views,
  #  "Using SQL and Pandas": using_sql_pandas
}

def main():
    col1, col2 = st.columns(2)

    with col1:
        st.image("./.streamlit/data_load_tool.png", width=250)

    with col2:
        st.title("Demo")

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]

    with st.spinner(f"Loading Page ..."):
        page.write()  # each page has a write function


if __name__ == "__main__":
    main()
