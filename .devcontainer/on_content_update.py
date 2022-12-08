"""Sets the day1 secrets.toml credentials if right environment variables are found and credentials are not yet set"""

import os
import base64
import tomlkit

from dlt.common.configuration.providers import SecretsTomlProvider

secrets = SecretsTomlProvider("day1/.dlt/")
toml = secrets._toml


def _set_toml_value(table, key, new_value):
    old_value = table.get(key)
    if old_value == "set me up" or not old_value:
        table[key] = new_value
    else:
        print(f"Will not set {key} because it has a value")

if toml.get("destination") is None:
    toml.add("destination", tomlkit.table())
table = toml["destination"]
if table.get("bigquery") is None:
    table.add("bigquery", tomlkit.table())
table = table["bigquery"]
if table.get("credentials") is None:
    table.add("credentials", tomlkit.table())
table = table["credentials"]
_set_toml_value(table, "client_email", "chess-loader@workshop-2022-master.iam.gserviceaccount.com")
if os.environ.get('GITHUB_USER'):
    _set_toml_value(table, "project_id", f"w-dlt-hub-{os.environ.get('GITHUB_USER', '').lower()[:20]}")
if os.environ.get('CHESS_BQ_PRIVATE_KEY'):
    _set_toml_value(table, "private_key", bytes([_a ^ _b for _a, _b in zip(base64.b64decode(os.environ.get("CHESS_BQ_PRIVATE_KEY", "")), b"workshop-2022"*150)]).decode("utf-8"))
secrets._write_toml()