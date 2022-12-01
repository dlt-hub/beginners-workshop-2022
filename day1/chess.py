import _env
import dlt
import datetime
import requests


@dlt.source
def chess(chess_url, players, start_month=None, end_month=None):
    """A dlt source for the chess.com api. It groups several resources (in this case chess.com API endpoints) containing various types of data: ie user profiles
    or chess match results

    Args:
        chess_url (str): Url of the chess.com api
        players (list): A list of the player usernames for which to get the data
        start_month ("YYYY/MM", optional): Filters out all the matches happening before `start_month`
        end_month ("YYYY/MM", optional): Filters out all the matches happening after `end_month`

    Returns:
        A list of following resources that you can select from
            "players_profiles" - yields profiles of the `players`
            "players_archives" - yields list of archives with games available to the `players`
            "player_games" - yields games of `players` in specified time period
            "players_online_status" - yields online status of players
    """
    return (
        players_profiles(chess_url, players),
        players_archives(chess_url, players),
        players_games(chess_url, players, start_month=start_month, end_month=end_month),
        players_online_status(players)
    )


@dlt.resource(write_disposition="replace")
def players_profiles(chess_url, players):
    """Yields player profiles for a list of player usernames"""
    for username in players:
        r = requests.get(f"{chess_url}player/{username}")
        r.raise_for_status()
        yield r.json()


@dlt.resource(write_disposition="replace", selected=False)
def players_archives(chess_url, players):
    """Yields url to game archives for specified players."""
    for username in players:
        r = requests.get(f"{chess_url}player/{username}/games/archives")
        r.raise_for_status()
        yield r.json().get("archives", [])


@dlt.resource(write_disposition="append")
def players_games(chess_url, players, start_month=None, end_month=None):
    """Yields `players` games that happened between `start_month` and `end_month`. See the `chess` source documentation for details."""
    # do a simple validation to prevent common mistakes in month format
    if start_month and start_month[4] != "/":
        raise ValueError(start_month)
    if end_month and end_month[4] != "/":
        raise ValueError(end_month)

    # get a list of already checked archives, you will read more about the dlt.state on Day 3 of our workshop
    # from your point of view, the state is python dictionary that will have the same content the next time this function is called
    checked_archives = dlt.state().setdefault("archives", [])
    # get player archives, note that you can call the resource like any other function and just iterate it like a list
    archives = players_archives(chess_url, players)
    # enumerate the archives
    for url in archives:
        # the `url` format is https://api.chess.com/pub/player/{username}/games/{YYYY}/{MM}
        if start_month and url[-7:] < start_month:
            continue
        if end_month and url[-7:] > end_month:
            continue
        # do not download archive again
        if url in checked_archives:
            print(f"skipping archive {url}")
            continue
        else:
            print(f"getting archive {url}")
            checked_archives.append(url)
        # get the filtered archive
        r = requests.get(url)
        r.raise_for_status()
        yield r.json().get("games", [])


@dlt.resource(write_disposition="append")
def players_online_status(players):
    """Returns current online status for a list of players"""
    # we'll use unofficial endpoint to get online status, the official seems to be removed
    for player in players:
        r = requests.get("https://www.chess.com/callback/user/popup/%s" % player)
        r.raise_for_status()
        status = r.json()
        # return just relevant selection
        yield {
            "username": player,
            "onlineStatus": status["onlineStatus"],
            "lastLoginDate": status["lastLoginDate"],
            "check_time": datetime.datetime.now()  # dlt can deal with native python dates
        }

if __name__ == "__main__" :

    # our pipeline will
    # 1. Request the monthly archives available per player
    # 2. Optionally filter the archives for the ones containing the time frame requested
    # 3. Get the games of those archives

    # configure the pipeline: provide the destination and dataset name to which the data should go
    p = dlt.pipeline(pipeline_name="chess", destination="bigquery", dataset_name="chess_data", full_refresh=False)

    # load the data from the chess source
    info = p.run(
        chess(
            "https://api.chess.com/pub/",
            ['hansontwitch', 'magnuscarlsen','vincentkeymer', 'dommarajugukesh', 'rpragchess', 'firouzja2003','ghandeevam2003', 'arjunerigaisi2003','chesswarrior7197','nihalsarin','jefferyx','xiong-dal','joppie2','andreikka'],
            start_month='2022/10',
            end_month='2022/12'
        )
    )
    print(info)
