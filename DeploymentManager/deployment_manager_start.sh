
        docker stop deployment_manager_container
        docker rm deployment_manager_container
        docker build -f deployment_manager_docker_file -t deployment_manager_img .
        docker container run -v /home/azureuser/logs:/logs -d --name deployment_manager_container -p 8030:8050 deployment_manager_img
    