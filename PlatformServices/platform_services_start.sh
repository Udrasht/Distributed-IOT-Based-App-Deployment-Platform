
        docker stop platform_services_container
        docker rm platform_services_container
        docker build -f platform_services_docker_file -t platform_services_img .
        docker container run -v /home/azureuser/logs:/logs -d --name platform_services_container -p 8110:8050 platform_services_img
    