
        docker stop node_manager_container
        docker rm node_manager_container
        docker build -f node_manager_docker_file -t node_manager_img .
        docker container run -v /home/azureuser/logs:/logs -d --name node_manager_container -p 8040:8050 node_manager_img
    