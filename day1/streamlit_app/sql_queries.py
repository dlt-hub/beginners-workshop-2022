import streamlit as st
import altair as alt

from _helpers import query_to_dataframe


def query_block(title,k, query='SELECT 1'):
    example_query = f"""-- get the usernames by player name, and then use them to find the match
            {query}
            """
    sql_query = st.text_area(title, value=example_query)
    if st.button("Run Query", key = k):
        if sql_query:
            st.text("Results of a query")
            try:
                # run the query from the text area
                df = query_to_dataframe(sql_query)
                # and display the results
                st.dataframe(df)

                try:
                    # now if the dataset has supported shape try to display the bar or altair chart
                    if df.dtypes.shape[0]==1:
                        # try barchart
                        st.bar_chart(df)
                    if df.dtypes.shape[0]==2:
                        # try altair
                        bar_chart = alt.Chart(df).mark_bar().encode(
                            x=f'{df.columns[1]}:Q',
                            y=alt.Y(f'{df.columns[0]}:N', sort='-x')
                        )
                        st.altair_chart(bar_chart, use_container_width=True)
                except Exception as ex:
                    st.error(f"Chart failed due to: {ex}")
            except Exception as ex:
                st.text("Exception when running query")
                st.exception(ex)

def write():

    # Both these guys are GMs so you need to load the data before you can query it.

    st.title("Scandalous games!")
    st.title("https://www.chess.com/blog/CHESScom/hans-niemann-report")

    query_block("What is the username of the alleged cheater named Hans Niemann?",1,
    query = 'select * from players_profiles where name like "%Niemann%" ')

    query_block("What was the match he cheated in against Magnus Carlsen? Find the url and replay the match.",
    2,query = 'select 1')



"""
-- shows how much you listened to your playlists
    SELECT m.*,  p1.name as player_1_name, 
from titled_user_matches__finished as m
left join titled_user_matches as um 
  on m._dlt_parent_id = um._dlt_id
-- let's do a self join on matches with the condition that the user is different, to get the other player
left join 
left join titled_user_profiles as p1
  on p.username = um.username

    """

