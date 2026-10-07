import docker


IMAGE_NAME = "flask-apparmor"
PROFILE_NAME = "my-apparmor-profile"


def main():
    client = docker.from_env()
    container = None

    try:
        container = client.containers.create(
            IMAGE_NAME,
            ports={"5000/tcp": 5000},
            security_opt=[f"apparmor={PROFILE_NAME}"],
        )
        container.start()
        print(f"Container started: {container.short_id}")

        tests = [
            (
                "Attempt to read /etc/passwd",
                ["python", "-c", "open('/etc/passwd').read()"],
            ),
            (
                "Attempt to execute /bin/bash",
                ["/bin/bash", "-c", "echo unrestricted"],
            ),
        ]
        for label, command in tests:
            result = container.exec_run(command)
            output = result.output.decode(errors="replace").strip()
            print(f"{label}: Exit Code {result.exit_code}, Output: {output}")
            if result.exit_code == 0:
                raise RuntimeError(f"Restricted action unexpectedly succeeded: {label}")

        print("Both restricted actions were denied")
    finally:
        if container is not None:
            try:
                container.stop()
            except docker.errors.APIError:
                pass
            container.remove(force=True)
            print("Container stopped and removed")
        client.close()


if __name__ == "__main__":
    main()