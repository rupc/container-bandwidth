from fabric import Connection, task

# Define remote hosts mapping (hostname to SSH user@host)
hosts = {
    "bsp-server-1": {"host": "root@bsp-server-1", "port": 2200},
    "bsp-server-4": {"host": "root@bsp-server-4", "port": 22},
}

@task
def exec_service(c, service_name, command):
    """
    Execute a command inside a container belonging to a Docker Swarm service.
    
    Args:
        c: Fabric connection object
        service_name (str): Name of the Docker Swarm service
        command (str): Command to execute inside the container
    """
    # 1. Find the node where the service is running
    print(f"Finding the node where the service '{service_name}' is running...")
    result = c.run(f"docker service ps {service_name} --filter 'desired-state=running' --format '{{{{.Node}}}}'", hide=True)
    node = result.stdout.strip()
    
    if not node:
        print(f"Error: No running task found for service '{service_name}'.")
        return

    print(f"Service '{service_name}' is running on node: {node}")

    # 2. Connect to the node where the service is running
    if node not in hosts:
        print(f"Error: No SSH configuration found for node '{node}'.")
        return

    remote_connection = Connection(hosts[node])

    # 3. Find the container ID of the running service
    print(f"Finding the container ID for service '{service_name}' on node '{node}'...")
    result = remote_connection.run(f"docker ps --filter 'name={service_name}' --format '{{{{.ID}}}}'", hide=True)
    container_id = result.stdout.strip()

    if not container_id:
        print(f"Error: No running container found for service '{service_name}' on node '{node}'.")
        return

    print(f"Found container '{container_id}' for service '{service_name}' on node '{node}'.")

    # 4. Execute the command inside the container
    print(f"Executing command '{command}' in container '{container_id}'...")
    remote_connection.run(f"docker exec {container_id} {command}")

@task
def run_iperf3(c, server_service, client_service):
    """
    Automate iperf3 bandwidth test between two Swarm services.

    Args:
        c: Fabric connection object
        server_service (str): Name of the Swarm service acting as iperf3 server
        client_service (str): Name of the Swarm service acting as iperf3 client
    """
    # Define the specific network name to fetch IP
    network_name = "mec"

    # 1. Find the node and container for the server service
    print(f"Finding server container for service '{server_service}'...")
    result = c.run(f"docker service ps {server_service} --filter 'desired-state=running' --format '{{{{.Node}}}}'", hide=True)
    server_node = result.stdout.strip()

    if not server_node or server_node not in hosts:
        print(f"Error: No running node found for server service '{server_service}'.")
        return

    ssh_config = hosts[server_node]
    server_connection = Connection(ssh_config["host"], port=ssh_config["port"])

    server_container = server_connection.run(
        f"docker ps --filter 'name={server_service}' --format '{{{{.ID}}}}'", hide=True
    ).stdout.strip()

    if not server_container:
        print(f"Error: No running container found for server service '{server_service}'.")
        return

    # Get the server container's IP address on the specified network
    server_ip = server_connection.run(
        f"docker inspect -f '{{{{.NetworkSettings.Networks.{network_name}.IPAddress}}}}' {server_container}",
        hide=True
    ).stdout.strip()

    print(f"Server container '{server_container}' is running on node '{server_node}' with IP '{server_ip}'.")

    # 2. Find the node and container for the client service
    print(f"Finding client container for service '{client_service}'...")
    result = c.run(f"docker service ps {client_service} --filter 'desired-state=running' --format '{{{{.Node}}}}'", hide=True)
    client_node = result.stdout.strip()

    if not client_node or client_node not in hosts:
        print(f"Error: No running node found for client service '{client_service}'.")
        return

    ssh_config = hosts[client_node]
    client_connection = Connection(ssh_config["host"], port=ssh_config["port"])

    client_container = client_connection.run(
        f"docker ps --filter 'name={client_service}' --format '{{{{.ID}}}}'", hide=True
    ).stdout.strip()

    if not client_container:
        print(f"Error: No running container found for client service '{client_service}'.")
        return

    print(f"Client container '{client_container}' is running on node '{client_node}'.")

    # 3. Start iperf3 server in the server container
    print(f"Starting iperf3 server in container '{server_container}' on node '{server_node}'...")
    server_connection.run(f"docker exec -d {server_container} iperf3 -s")

    # 4. Run iperf3 client in the client container
    print(f"Running iperf3 client in container '{client_container}' on node '{client_node}'...")
    result = client_connection.run(
        f"docker exec {client_container} iperf3 -c {server_ip} -t 5",
        hide=True
    )
    print(f"iperf3 client output:\n{result.stdout}")

    # 5. Stop iperf3 server
    print(f"Stopping iperf3 server in container '{server_container}'...")
    server_connection.run(f"docker exec {server_container} pkill iperf3")
