
        docker stop authenticator_container
        docker rm authenticator_container
        docker build -f authenticator_docker_file -t authenticator_img .
        docker container run -v /home/azureuser/logs:/logs -d --name authenticator_container -p 8020:8050 authenticator_img
    