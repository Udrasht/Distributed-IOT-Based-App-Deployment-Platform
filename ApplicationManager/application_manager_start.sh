
        docker stop application_manager_container
        docker rm application_manager_container
        docker build -f application_manager_docker_file -t application_manager_img .
        docker container run -v /home/azureuser/logs:/logs -d --name application_manager_container -p 8010:8050 application_manager_img
    