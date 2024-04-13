@echo off

echo Stopping test-postgres containing if running
docker stop test-postgres

echo Removing test-progres container if it exists
docker rm test-postgres

rem docker command to build a new image
rem Tag the image with the name "custom-test-postgres"
rem The build context is the current directory (indicated by ".")
echo Building new Docker image named "custom-test-postgres"
docker build --no-cache -t custom-test-postgres .
rem Docker command to run a container
rem --name: Assign a name to the container as "test-postgres"
rem --env-file: Specify a file that contains environment variables to be passed to the container
rem -e POSTGRES_USER=myuser and -e POSTGRES_PASSWORD=mypassword: set the PostgreSQL superuser's username and password, respectively.
rem -d: Run the container in detached mode which means it runs in the background and doesn't output logs to the terminal
rem -p: Publish the container’s port(s) 5432 to the host 5432
rem (last line): Specify the name of the docker image to run
echo Running the Docker container named "test-postgres"
docker run --name test-postgres --env-file ./setup.env -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -d -p 5432:5432 custom-test-postgres

echo Done
pause