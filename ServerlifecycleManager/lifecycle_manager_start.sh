
        docker stop lifecycle_manager_container
        docker rm lifecycle_manager_container
        docker build -f lifecycle_manager_docker_file -t lifecycle_manager_img .
        docker container run -v /home/azureuser/logs:/logs -d --name lifecycle_manager_container -p 8080:8050 lifecycle_manager_img
    