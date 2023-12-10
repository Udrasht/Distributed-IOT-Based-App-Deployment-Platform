
        docker stop load_balancer_container
        docker rm load_balancer_container
        docker build -f load_balancer_docker_file -t load_balancer_img .
        docker container run -v /home/azureuser/logs:/logs -d --name load_balancer_container -p 8110:8050 load_balancer_img
    