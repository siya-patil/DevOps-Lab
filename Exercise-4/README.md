# Exercise 4: Docker Networking with Multiple Containers

## Objective

Create a user-defined Docker bridge network and run a Flask API, MySQL, and Redis on it. Verify host-to-container port publishing, container-name DNS, and service connectivity.

All evidence below was captured while running this exercise on Linux with Docker Engine 29.8.0 on 2026-10-07. Docker-assigned IDs and IP addresses can differ on another run.

## Files

- [app.py](app.py): Flask API with a `GET /about` endpoint.
- [requirements.txt](requirements.txt): pinned Flask and compatible Werkzeug dependencies.
- [Dockerfile](Dockerfile): builds the Flask API image.

Flask binds to `0.0.0.0` inside the container so Docker's published host port can reach it. Werkzeug is pinned because Flask 2.0.1 is incompatible with some newer Werkzeug releases.

## 1. Verify Docker

```bash
docker --version
docker info --format '{{.ServerVersion}}'
docker ps
```

Captured output:

```text
Docker version 29.8.0, build 88096ef
29.8.0
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

## 2. Create and Inspect the Bridge Network

```bash
docker network create --driver bridge my-bridge-net
docker network ls --filter name=my-bridge-net
docker network inspect my-bridge-net
```

Captured network ID:

```text
1a0f67570f4790819d1b871634f14690746225422b79d14c4a1ec59a8a274d74
```

Captured network list:

```text
NETWORK ID     NAME            DRIVER    SCOPE
1a0f67570f47   my-bridge-net   bridge    local
```

Captured inspect details (Docker selected this subnet for this run):

```text
Name=my-bridge-net Driver=bridge Subnet=172.18.0.0/16 Gateway=172.18.0.1
```

The subnet and addresses are dynamically allocated; do not rely on these exact values.

## 3. Build the Flask Image

From this directory, build the image:

```bash
docker build -t flask-api .
docker images --filter reference=flask-api
```

The build completed successfully. Captured image:

```text
REPOSITORY   TAG       IMAGE ID       SIZE
flask-api    latest    241fc2b9c6c8   200MB
```

## 4. Launch the Three Containers

Start MySQL with an explicit root password and database. The password below is only for this local lab; do not use it for a real deployment.

```bash
docker run -d --name mysql --network my-bridge-net \
	-e MYSQL_ROOT_PASSWORD=rootpass \
	-e MYSQL_DATABASE=devopsdb mysql:latest

docker run -d --name redis --network my-bridge-net redis:latest

docker run -d --name flask --network my-bridge-net \
	-p 5001:5001 flask-api
```

Captured container IDs:

```text
mysql: 35d0a945954a
redis: bfd873a9d118
flask: e5fff6df96f7
```

Captured running state:

```text
NAMES     IMAGE          STATUS          PORTS
flask     flask-api      Up              0.0.0.0:5001->5001/tcp
redis     redis:latest   Up              6379/tcp
mysql     mysql:latest   Up              3306/tcp, 33060/tcp
```

The `Up` status and MySQL query below confirm that initialization completed. MySQL and Redis ports are not published to the host; Flask reaches them over the Docker network.

## 5. Verify Host-to-Flask Access

```bash
docker port flask
curl -fsS http://localhost:5001/about
```

Captured port mapping and API response:

```text
5001/tcp -> 0.0.0.0:5001
5001/tcp -> [::]:5001
{"description":"This is a simple REST API built with Flask.","name":"Simple REST API","version":"1.0"}
```

The port mapping publishes the Flask container's port 5001 on host port 5001.

## 6. Verify Network Membership and Service Discovery

```bash
docker network inspect --format \
	'Name={{.Name}} Driver={{.Driver}} Subnet={{(index .IPAM.Config 0).Subnet}} Gateway={{(index .IPAM.Config 0).Gateway}}{{range .Containers}}\nContainer={{.Name}} IPv4={{.IPv4Address}}{{end}}' \
	my-bridge-net

docker exec flask getent hosts mysql redis
```

Captured network details:

```text
Name=my-bridge-net Driver=bridge Subnet=172.18.0.0/16 Gateway=172.18.0.1
Container=mysql IPv4=172.18.0.2/16
Container=redis IPv4=172.18.0.3/16
Container=flask IPv4=172.18.0.4/16
```

Captured Docker DNS results:

```text
172.18.0.2      mysql
172.18.0.3      redis
```

The `python:3.9-slim` image does not include `ping` by default. `getent hosts` verifies Docker's embedded DNS without installing extra packages. A direct TCP check from Flask also succeeded:

```text
mysql:3306 reachable
redis:6379 reachable
```

## 7. Verify Redis and MySQL

```bash
docker exec redis redis-cli ping
docker exec mysql mysql -uroot -prootpass -e 'SHOW DATABASES;'
```

Captured Redis response:

```text
PONG
```

Captured MySQL databases:

```text
Database
devopsdb
information_schema
mysql
performance_schema
sys
```

## 8. Clean Up

Stop and remove the containers, then remove the custom network:

```bash
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net
```

Captured cleanup output:

```text
mysql
redis
flask
mysql
redis
flask
my-bridge-net
```

The `flask-api` image was left available locally; remove it separately with `docker rmi flask-api` if desired. Avoid `docker system prune` unless you intend to remove other unused Docker resources too.

## Questions and Answers

1. **What is the purpose of `--network` (or `--net`)?** It attaches a container to the selected Docker network. `--network` is the modern, clearer spelling.
2. **How do containers communicate on the same user-defined bridge?** They connect to each other's container/service names using Docker's embedded DNS, then communicate directly over container ports. Names are more stable than container IP addresses.
3. **What is the difference between bridge and host networking?** A bridge network gives containers their own network namespace and connects them through Docker's bridge. Host networking shares the host network namespace and does not provide the same network isolation; behavior varies by operating system.
4. **How do you expose a container port to the host?** Publish it with `-p HOST_PORT:CONTAINER_PORT`, as in `-p 5001:5001`. Publishing is not required for communication between containers on the same network.

## Final Takeaways

- A user-defined bridge network provides isolation and name-based service discovery.
- Flask listens on `0.0.0.0:5001` inside its container; `-p 5001:5001` publishes that service to the host.
- Flask can reach MySQL and Redis by their container names without publishing ports 3306 or 6379.
- Explicit dependency versions and MySQL initialization settings make the lab more repeatable.
