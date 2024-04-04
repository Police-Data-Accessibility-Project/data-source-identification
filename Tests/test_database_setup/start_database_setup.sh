# Stop the container if it is running
docker stop test-postgres

# Remove the container
docker rm test-postgres

# docker command to build a new image
# Tag the image with the name "custom-test-postgres"
# The build context is the current directory (indicated by ".")
docker build --no-cache \
-t custom-test-postgres \
.

# Docker command to run a container
# --name: Assign a name to the container as "test-postgres"
# --env-file: Specify a file that contains environment variables to be passed to the container
# -e POSTGRES_USER=myuser and -e POSTGRES_PASSWORD=mypassword: set the PostgreSQL superuser's username and password, respectively.
# -d: Run the container in detached mode which means it runs in the background and doesn't output logs to the terminal
# -p: Publish the container’s port(s) 5432 to the host 5432
# (last line): Specify the name of the docker image to run
docker run \
--name test-postgres \
--env-file ./setup.env \
-e POSTGRES_USER=myuser \
-e POSTGRES_PASSWORD=mypassword \
-d \
-p 5432:5432 \
custom-test-postgres