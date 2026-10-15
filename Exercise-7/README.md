# Exercise 7: Jenkins CI Installation

## Objective

Install Jenkins using Docker, verify the service and published ports, retrieve the initial administrator unlock password from the container, and access the Jenkins setup page.

Evidence below was captured on Linux with Docker Engine 29.8.0 on 2026-10-15. The Jenkins container remains running so the setup can be continued at [http://localhost:8080](http://localhost:8080).

## Files

- [compose.yaml](compose.yaml): starts the official Jenkins LTS image, publishes its web and agent ports on localhost, and persists Jenkins state in a named volume.
- [screenshots/jenkins-unlock.png](screenshots/jenkins-unlock.png): captured Jenkins initial unlock screen.

The repository walkthrough uses `docker run` with `jenkins/jenkins:lts`. This exercise uses Docker Compose for the same image and ports, while adding a named volume so Jenkins configuration survives container recreation. Ports are bound to `127.0.0.1` rather than every host interface.

## 1. Validate the Compose Configuration

```bash
docker compose config --quiet
```

Captured result: exit code `0`; no configuration errors were reported.

## 2. Start Jenkins

From this directory:

```bash
docker compose up -d
```

Captured result:

```text
[+] up 4/4
Image jenkins/jenkins:lts      Pulled
Volume exercise-7_jenkins-home Created
Network exercise-7_default     Created
Container jenkins-exercise-7   Started
```

## 3. Verify the Container and Ports

```bash
docker compose ps
```

Captured result:

```text
NAME                 IMAGE                 STATUS         PORTS
jenkins-exercise-7   jenkins/jenkins:lts   Up             127.0.0.1:8080->8080/tcp, 127.0.0.1:50000->50000/tcp
```

The exact container ID from this run was `8ebbf0811773`. The Jenkins image resolved to image ID `sha256:a660310e39ade10631f774bacd5219de767dfd08947ea5c32a739b5e5bb382c1`.

Jenkins reported version `2.580.1`, running on OpenJDK `21.0.12.1`:

```text
Starting version 2.580.1
openjdk version "21.0.12.1" 2026-08-18 LTS
Jenkins is fully up and running
```

## 4. Retrieve the Initial Administrator Password

Jenkins generated its initial unlock password at:

```text
/var/jenkins_home/secrets/initialAdminPassword
```

Verify that the file exists without printing its contents:

```bash
docker exec jenkins-exercise-7 sh -c \
  'test -s /var/jenkins_home/secrets/initialAdminPassword && echo "Initial admin password file exists (value withheld)"'
```

Captured result:

```text
Initial admin password file exists (value withheld)
Initial password file bytes: 33
```

To unlock Jenkins on this machine, display the generated password directly in your terminal and paste it into the browser prompt:

```bash
docker exec jenkins-exercise-7 cat /var/jenkins_home/secrets/initialAdminPassword
```

This password grants administrator setup access. Do not add it to the README, source control, or screenshots. The value is intentionally redacted from all captured evidence.

## 5. Access the Jenkins Setup Page

Open [http://localhost:8080](http://localhost:8080). Jenkins responded successfully:

```text
Jenkins login endpoint: HTTP 200
```

The captured browser page displayed **Unlock Jenkins** and pointed to the initial password file above. Screenshot evidence:

![Jenkins initial unlock screen showing the password file location](screenshots/jenkins-unlock.png)

After entering the local unlock password, Jenkins will offer suggested plugins and creation of the first administrator account. Those account details are intentionally left for the owner to choose and are not stored in this repository.

## Cleanup

Jenkins is left running for the setup to continue. To stop and remove the container/network while preserving Jenkins data:

```bash
docker compose down
```

To also delete the named Jenkins home volume and its saved configuration:

```bash
docker compose down -v
```