
        docker stop sensor_manager_container
        docker rm sensor_manager_container
        docker build -f sensor_manager_docker_file -t sensor_manager_img .
        docker container run -d --name sensor_manager_container -p 8060:8050 sensor_manager_img
    