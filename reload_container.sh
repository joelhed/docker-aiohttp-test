CONT_ID=`docker ps -qn 1`
docker rm -f $CONT_ID
make build
make run-detached
