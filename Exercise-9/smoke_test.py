import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def main(url: str) -> None:
    for _ in range(30):
        try:
            with urlopen(url, timeout=2) as response:
                body = response.read().decode("utf-8")
                if response.status != 200:
                    raise AssertionError(f"Unexpected HTTP status: {response.status}")
                if body != "Hello, Jenkins Multi-Stage Pipeline!":
                    raise AssertionError(f"Unexpected response body: {body!r}")
                print(f"HTTP {response.status}: {body}")
                return
        except (URLError, TimeoutError):
            time.sleep(1)

    raise RuntimeError(f"Application did not become ready at {url}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18089/")