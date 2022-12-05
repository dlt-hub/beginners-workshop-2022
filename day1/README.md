# The chess.com API pipeline
This pipeline loads the same data that was used in the [report](https://www.chess.com/blog/CHESScom/hans-niemann-report) investigating the alleged frauds by Hans Niemann. We load the archive of games of 8 Grand Masters (inclusing Magnus Carlson) and their player's strength scores to find some unusual patterns.

# Running the pipeline
If you signed up to the workshop and you have your BigQuery link you can run the pipeline right away
```
cd day1
python3 chess.py
```

If you are not signed up for the workshop you need to put your BigQuery credentials in the `.dlt/secrets.toml`
```toml
[destination.bigquery.credentials]
client_email = "chess-loader@workshop-2022-master.iam.gserviceaccount.com"
# private_key = "set me up"
# project_id = "set me up"
```

# Seeing the data
Head up to the BigQuery project using the link you've got in the invitation e-mail and look for `chess_data` dataset.

# Loading status in streamlit app
Launch the streamlit app `streamlit run streamlit_app/main.py`.

1. Codespaces will show you a popup on which you can click to open the web app
2. **It takes some time for the codespaces to open the HTTP port so you may want to reload the page a few times**