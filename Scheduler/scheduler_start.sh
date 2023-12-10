
        docker stop scheduler_container
        docker rm scheduler_container
        docker build -f scheduler_docker_file -t scheduler_img .
        docker container run -v /home/azureuser/logs:/logs -d --name scheduler_container -p 8100:8050 scheduler_img
    