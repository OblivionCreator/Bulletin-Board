docker prune
docker build -t bulletin-board .
docker save mettaton-2 -o ~/docker-store/bulletin-board.tar