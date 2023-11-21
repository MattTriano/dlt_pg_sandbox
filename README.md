# dlt dbt Postgres Pipeline

## Setup

I created a conda env with most of the regular stuff I use and then used pip to install dlt.

I also created a `docker-compose.yml` file and `Dockerfile` for a PostGIS image, and started it up.

Then I started creating a filesystem-to-postgres dlt pipeline

```bash
mkdir data
mkdir pipelines && cd pipelines
dlt init filesystem postgres
```

Then I modified `/pipelines/.dlt/config.toml` so `bucket_url="../../data"`
And I modified `secrets.toml`, entering in the database pw, username, hostname, etc set in the `docker-compose.yml` file.

