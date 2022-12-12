import requests
import dlt

TWITTER_API_URL = "https://api.twitter.com/2/tweets/%s"


@dlt.source(max_table_nesting=2)
def twitter_data(search_terms, start_time=None, end_time=None, api_secret_key=dlt.secrets.value):
    return search_tweets(search_terms, start_time=start_time, end_time=end_time, api_secret_key=api_secret_key)


def _headers(api_secret_key):
    """Constructs Bearer type authorization header as required by twitter api"""
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


# explain the `dlt.resource` and the default table naming, write disposition etc.
@dlt.resource(write_disposition="append")
def search_tweets(search_terms, start_time=None, end_time=None, api_secret_key=dlt.secrets.value):
    headers = _headers(api_secret_key)
    # get search results for each term
    for search_term in search_terms:
        params = {
            'query': search_term,
            'max_results': 20,  # maximum elements per page: we set it to low value to demonstrate the paginator
            'start_time': start_time,  # '2022-11-08T00:00:00.000Z',
            'end_time': end_time,  # '2022-11-09T00:00:00.000Z',
            # basic twitter fields to be included in the data
            # 'tweet.fields': 'id,text,author_id,geo,created_at,lang,public_metrics,source',
            # uncomment below to include annotations and entities as described here: https://developer.twitter.com/en/docs/twitter-api/annotations/overview
            'tweet.fields': 'id,text,author_id,geo,created_at,lang,public_metrics,source,context_annotations,entities',
            # optional expansions with data related to returned tweets
            'expansions': 'author_id,geo.place_id',
            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
            'place.fields': 'full_name,id,country,country_code,geo,name,place_type'
        }

        # get all the pages
        for page in _paginated_get(TWITTER_API_URL % "search/recent", headers, params):
            meta = page["meta"]
            # ignore pages without results
            if meta["result_count"] > 0:
                # add the search term that produced given page to the results
                page['search_term'] = search_term
                # remove the meta, we do not need to store it
                del page["meta"]
                # move all "expansions" to the page for nicer structure
                expansions = page.pop("includes", {})
                for k, v in expansions.items():
                    page[k] = v
                # yield the modified page to be loaded by dlt
                yield page



if __name__=='__main__':
    search_terms = ['python data engineer job']

    dataset_name = 'tweets'

    # init your pipeline and destination
    p = dlt.pipeline(
                    pipeline_name="twitter_performance_hints",
                    destination="bigquery",
                    dataset_name="twitter_performance_hints",
                    # export the schema to this folder
                    export_schema_path="schema_performance_hints/export",
                    # import the schema from this folder, mind that this folder will be initialized with a schema for you
                    import_schema_path="schema_performance_hints/import",
                    # use full refresh while you experiment with your schema
                    full_refresh=False
                )

    # how to proceed
    # 1. run for the first time
    # 2. look at the export and import schema. let's say that we want 1. use _dlt_load_id as cluster for all tables 2. use created_at as partition on twitter__data table
    # 3. in the import schema we add the following in propagation section
    """
    propagation:
        root:
          _dlt_load_id: _dlt_load_id  # propagate _dlt_load_id from parent to all child tables
        tables:
          search_tweets__data:
            created_at: created_at  # propagate created_at from search_tweets__data to all child tables of it

    """
    #  4. in the import schema we add the following to the default hints
    """
    cluster:
    - _dlt_load_id  # all columns with this name are cluster columns
    partition:
    - created_at  # all columns with this name are partition columns
    """
    # 5. run again and go to exported schema and see that all columns are propagated and have the desired hints
    # 6. you can uncomment the run and commend out the full_refresh and see the tables in bigquery
    # 7. you can actually push import schema to github!

    # extract the twitter data to obtain initial schema
    p.extract(twitter_data(search_terms=search_terms))
    # normalize and package the data to infer the exact schema from data
    p.normalize()
    # no need to load to the data to modify the import schema and put propagation there
    print(p.run())


