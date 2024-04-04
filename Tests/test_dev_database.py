from pytest_postgresql import factories

"""
This requires a postgresql docker container set up and listening on port 5432 with the password "mysecretpassword"
If you don't already have it installed in docker, run `docker pull postgres`
Then, run the following command:
docker run -p 5432:5432 --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
With that up and running, the below code should work
TODO: Move this to a README, Max
"""
#
postgresql_in_docker = factories.postgresql_noproc(port="5432", password="mypassword")
postgresql = factories.postgresql("postgresql_in_docker", dbname="test")

def test_get_agencies_without_homepage_urls(postgresql):
    cur = postgresql.cursor()
    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")