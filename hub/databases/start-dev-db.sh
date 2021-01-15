docker run --name dev-postgres -e POSTGRES_PASSWORD=password -d -p 6543:5432 postgres
echo waiting 15 seconds for the container to start up
sleep 15
echo waiting over!
INIT_COMMANDS=$(cat ./schemas/pg.sql)
DEMO_COMMANDS=$(cat ./schemas/pg_demo_data.sql)
PGPASSWORD=password psql -h localhost -p 6543 -U postgres <<- EOSQL
	$INIT_COMMANDS
	$DEMO_COMMANDS
EOSQL
