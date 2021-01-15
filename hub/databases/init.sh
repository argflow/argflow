#!/bin/bash
set -e

INIT_COMMANDS=$(cat ./schemas/pg.sql)
DEMO_COMMANDS=$(cat ./schemas/pg_demo_data.sql)

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    $INIT_COMMANDS
	$DEMO_COMMANDS
EOSQL
