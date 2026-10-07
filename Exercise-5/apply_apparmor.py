import time
from urllib.request import urlopen

import docker


IMAGE_NAME = "flask-apparmor"
PROFILE_NAME = "my-apparmor-profile"


def main():
    client = docker.from_env()
    container = None

    try:
        print("Building image from Dockerfile...")
        client.images.build(path=".", tag=IMAGE_NAME)

        print("Running container with AppArmor profile...")
        container = client.containers.create(
            IMAGE_NAME,
            ports={"5000/tcp": 5000},
            security_opt=[f"apparmor={PROFILE_NAME}"],
        )
        container.start()
        print(f"Container started: {container.short_id}")

        for _ in range(20):
            try:
                with urlopen("http://127.0.0.1:5000/", timeout=2) as response:
                    print(f"HTTP response: {response.status} {response.read().decode()}")
                break
            except OSError:
                time.sleep(0.5)
        else:
            raise RuntimeError("Flask did not become ready on http://127.0.0.1:5000/")

        container_info = client.api.inspect_container(container.id)
        security_options = container_info["HostConfig"].get("SecurityOpt") or []
        if f"apparmor={PROFILE_NAME}" not in security_options:
            raise RuntimeError(f"Expected AppArmor profile not found: {security_options}")
        print(f"AppArmor profile applied: {security_options}")

        container.stop()
        print("Container stopped")
    finally:
        if container is not None:
            container.remove(force=True)
        client.close()


if __name__ == "__main__":
    main()