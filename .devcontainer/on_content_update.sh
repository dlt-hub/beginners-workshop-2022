#!/usr/bin/env bash

set -e
set -u


pip3 install -U python-dlt[bigquery]
python3 .devcontainer/on_content_update.py
