import os

# internal!
# create environment variable to hold the project id for the chess pipeline, we require this to send data to the right bigquery instance
# and it is only required for day 1. on day 2 you use your personal big query credentials.
os.environ["DESTINATION__BIGQUERY__CREDENTIALS__PROJECT_ID"] = f"w-dlt-hub-{os.environ['GITHUB_USER'].lower()[:20]}"