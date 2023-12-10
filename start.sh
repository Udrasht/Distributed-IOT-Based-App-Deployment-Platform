# docker build -f PlatformInitializer/platform_init_docker_file -t platform_init_docker_img .
# # -p 7070:80	Map TCP port 80 in the container to port 8080 on the Docker host.
# docker container run -p 7070:80 platform_init_docker_img

python3 ./PlatformInitializer/main.py