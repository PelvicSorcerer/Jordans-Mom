function Build {
    docker build -t jordans-mom .
}

Build -ErrorAction Stop
docker stop jordans-mom-container
docker rm jordans-mom-container
docker run --name jordans-mom-container --mount source=bot-files,target=/app/Audio jordans-mom