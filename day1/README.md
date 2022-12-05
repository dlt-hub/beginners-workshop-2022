# The chess.com API pipeline
This pipeline loads the same data that was used in the [report](https://www.chess.com/blog/CHESScom/hans-niemann-report) investigating the alleged frauds by Hans Niemann. We load the archive of games of 8 Grand Masters (inclusing Magnus Carlson) and their player's strength scores to find some unusual patterns.

# Running the pipeline
If you signed up to the workshop and you have your BigQuery link you can run the pipeline right away
```
cd day1
python3 chess.py
```

# Seeing the data
Head up to the BigQuery project using the link you've got in the invitation e-mail and look for `chess_data` dataset.

# Loading status in streamlit app
Launch the streamlit app `streamlit run streamlit_app/main.py`.

1. Codespaces will show you a popup on which you can click to open the web app
2. **It takes some time for the codespaces to open the HTTP port so you may want to reload the page a few times**


# Troubleshooting

## I get the following exception when running `chess.py`

`google.api_core.exceptions.NotFound: 404 POST https://bigquery.googleapis.com/bigquery/v2/projects/w-dlt-hub-rudolfix7/jobs?prettyPrint=false: Not found: Project w-dlt-hub-`**my-github-handle**

If you are not signed up for the workshop or you are connecting to codespaces with account different than provided during signup.

**You need to put your BigQuery credentials** in the `.dlt/secrets.toml`
```toml
[destination.bigquery.credentials]
client_email = "chess-loader@workshop-2022-master.iam.gserviceaccount.com"
# private_key = "set me up"
# project_id = "set me up"
```

**You need to comment all the lines in the**  `streamlit_app/_env.py`

## I get the following exception when running `chess.py`
`google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects/set%20me%20up/jobs?prettyPrint=false: Invalid project ID 'set me up'. Project IDs must contain 6-63 lowercase letters, digits, or dashes. Some project IDs also include domain name separated by a colon. IDs must start with a letter and may not end with a dash.`

You are running the pipeline outside of codespaces. **You need to follow the same steps as in the case above** 