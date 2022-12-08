import dlt
import requests


@dlt.source
def twitter_source(api_secret_key=dlt.secrets.value):
    return twitter_resource(api_secret_key)


def _create_auth_headers(api_secret_key):
    """Constructs Bearer type authorization header which is the most common authorization method"""
    headers = {
        "Authorization": f"Bearer {api_secret_key}"
    }
    return headers

def _paginated_get(url, headers, params, max_pages=5):
    """Requests and yields up to `max_pages` pages of results as per twitter api documentation: https://developer.twitter.com/en/docs/twitter-api/pagination"""
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page = response.json()
        # show the pagination info
        meta = page["meta"]
        print(meta)

        yield page

        # get next page token
        next_token = meta.get('next_token')
        max_pages -= 1

        # if no more pages or we are at the maximum
        if not next_token or max_pages == 0:
            break
        else:
            # set the next_token parameter to get next page
            params['pagination_token'] = next_token


@dlt.resource(write_disposition="append")
def twitter_resource(search_terms, start_time=None, end_time=None, api_secret_key=dlt.secrets.value):
    headers = _create_auth_headers(api_secret_key)
    # get search results for each term
    for search_term in search_terms:
        params = {  'query': search_term,
                'start_time': start_time,  # '2022-11-08T00:00:00.000Z',
                'end_time': end_time,  # '2022-11-09T00:00:00.000Z',
                'expansions': 'author_id',
                'tweet.fields': 'context_annotations,id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                'user.fields': 'id,name,username,created_at,description,public_metrics,verified'}
        url = "https://api.twitter.com/2/tweets/search/recent"

        # make request
        response = _paginated_get(url, headers=headers, params=params)
        for row in response:
            row['search_term'] = search_term
            yield row

if __name__=='__main__':
    search_terms = ['python data engineer']

    # search last hour of tweets
    from datetime import datetime, timedelta, timezone

    data_interval_start = datetime.now(timezone.utc) - timedelta(hours=3)
    data_interval_end = datetime.now(timezone.utc) - timedelta(hours=2)

    # format to twitter spec
    start_time = data_interval_start.isoformat()
    end_time = data_interval_end.isoformat()

    data = list(twitter_resource(search_terms=search_terms, start_time=start_time, end_time=end_time))

    print(data)

    exit()
    pipeline = dlt.pipeline(pipeline_name='twitter', destination='bigquery', dataset_name='twitter_data')

    # run the pipeline with your parameters and print the outcome
    load_info = pipeline.run(twitter_source(search_terms=search_terms, start_time=start_time, end_time=end_time))

    print(load_info)
    print(f'data interval: {data_interval_start} to {data_interval_end}')