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
def twitter_resource(api_secret_key=dlt.secrets.value):
    headers = _create_auth_headers(api_secret_key)
    search_term = 'data engineering'
    params = {'query': search_term}
    url = "https://api.twitter.com/2/tweets/search/recent"
    # make request
    response = _paginated_get(url, headers=headers, params=params)
    for row in response:
        row['search_term'] = search_term
        yield row


if __name__=='__main__':
    # configure the pipeline with your destination details
    pipeline = dlt.pipeline(pipeline_name='twitter', destination='bigquery', dataset_name='twitter_data')

    # print credentials by running the resource
    import json

    for row in twitter_resource():
        print(json.dumps(row, indent=2))

    exit()

    # run the pipeline with your parameters
    load_info = pipeline.run(twitter_source())

    # pretty print the information on data that was loaded
    print(load_info)
