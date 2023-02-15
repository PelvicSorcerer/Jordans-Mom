function Build {
    docker build -t jordans-mom .
}

$bottoken = Get-Content .\token.txt -Raw

Build -ErrorAction Stop
docker stop jordans-mom-container
docker rm jordans-mom-container
docker run -e BOT_TOKEN=$bottoken --name jordans-mom-container --mount source=bot-files,target=/app/Audio jordans-mom