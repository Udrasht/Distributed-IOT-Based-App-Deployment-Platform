
        docker stop sensor_manager_container
        docker rm sensor_manager_container
        docker build -f sensor_manager_docker_file -t sensor_manager_img .
        docker container run -v /home/azureuser/logs:/logs -d --name sensor_manager_container -p 8060:8050 sensor_manager_img
    