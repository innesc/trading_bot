## Steps to run as volume

If running in trading bot folder

`$ docker run --name v2_trade -v$(pwd)/app:/app --env-file .env bash`

Steps for building docker image

`docker --debug build . -t v2_trade`

