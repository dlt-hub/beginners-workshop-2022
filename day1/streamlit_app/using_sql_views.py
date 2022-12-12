import streamlit as st

from _helpers import query_to_dataframe, run_sql, to_fully_qualified_name


def write():


    ## view
    # the games table is arranged by white/black player
    # The view below creates a list of games by player rather than by color,
    # which will allow us to easily analyse the player's games

    players_games_table_name = to_fully_qualified_name("players_games")
    players_profiles_table_name = to_fully_qualified_name("players_profiles")

    unified_view = f"""with games as 
    -- reflect the games so we can join to either side with ease.
      (SELECT distinct url, 
        end_time, 
        black__rating as player_rating, 
        black__username as player_username,
        black__result as player_result,
        white__rating as opponent_rating,
        white__username as opponent_username,
        white__result as opponent_result
      FROM {players_games_table_name}
      union distinct
      SELECT distinct url, 
        end_time, 
        white__rating as player_rating, 
        white__username as player_username,
        white__result as player_result,
        black__rating as opponent_rating,
        black__username as opponent_username,
        black__result as opponent_result
      FROM {players_games_table_name}
      ),
    view_player_games as (select distinct p.username, 
    g.url,
    g.end_time,
    g.player_rating,
    g.opponent_rating,
    g.player_result,
    g.opponent_result,
    from {players_profiles_table_name} p
    inner join games as g
      on lower(g.player_username) = lower(p.username))
    select * from view_player_games
    """

    run_sql(f"create or replace view view_player_games as {unified_view}")

    st.header("However, not all questions can easily be answered from a raw table.")

    st.header("You might need to remodel your data to write the queries you need...")

    msg = """
    The following view re-arranges how games are stored. Originally they are stored by white/black player. 
    For analysis, we need them stored by player/opponent. 
    To achieve this, we join the games to the players twice, once on "black username" and once on "white username"
    """
    st.write(msg)

    df = query_to_dataframe("select * from view_player_games limit 100")
    st.dataframe(df)
    st.write("""This view can now be used to analyse the games.""")

    st.header("Now that we have this view. Here are some questions we can answer...")

    ratings_by_time = f"""
    SELECT username, 
    date_trunc(end_time, month) as date_,  
    avg(player_rating) as rating,
    FROM view_player_games
    group by 1,2
    """
    st.subheader("How rating of our selected grand masters change over time?")
    df = query_to_dataframe(ratings_by_time)
    st.dataframe(df)
