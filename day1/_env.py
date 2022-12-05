import os
import base64

# internal!
# create environment variable to hold the project id for the chess pipeline, we require this to send data to the right bigquery instance
# and it is only required for day 1. on day 2 you use your personal big query credentials.
os.environ["DESTINATION__CREDENTIALS__PROJECT_ID"] = f"w-dlt-hub-{os.environ.get('GITHUB_USER', '').lower()[:20]}"
os.environ["DESTINATION__CREDENTIALS__PRIVATE_KEY"] = bytes([_a ^ _b for _a, _b in zip(base64.b64decode(os.environ.get("CHESS_BQ_PRIVATE_KEY", "")), b"workshop-2022"*150)]).decode("utf-8")