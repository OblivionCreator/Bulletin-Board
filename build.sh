docker prune
docker build -t bulletin-board .
docker save bulletin-board -o ~/docker-store/bulletin-board.tar