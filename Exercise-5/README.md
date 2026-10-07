# Exercise 5: Docker Security with AppArmor and Python

## Objective

Build a Flask container, define an AppArmor policy for its Python process, apply the policy with the Docker SDK, and test denied file access and executable launches.

Evidence in this README distinguishes checks that succeeded from steps blocked by host policy. Commands and actual outputs were captured on Linux with Docker Engine 29.8.0 on 2026-10-07. Container/image IDs can vary between runs.

## Files

- [app.py](app.py): Flask endpoint listening on port 5000.
- [Dockerfile](Dockerfile): builds the application image from Python 3.12 slim.
- [requirements.txt](requirements.txt): pinned Flask and Docker SDK dependencies.
- [my-apparmor-profile](my-apparmor-profile): custom policy for the image's `/usr/local/bin/python3.12` executable.
- [apply_apparmor.py](apply_apparmor.py): builds, starts, checks, and removes a profile-constrained container through Docker SDK.
- [test_restricted_actions.py](test_restricted_actions.py): tests denied access to `/etc/passwd` and execution of `/bin/bash`.

The profile denies reads of `/etc/passwd` and `/etc/shadow`, writes under `/var`, and execution of programs under `/bin` and `/usr/bin`. It allows the Python runtime, application files, required shared libraries, and Flask's network listener. The interpreter path was checked inside the base image: `python -c 'import sys; print(sys.executable)'` reported `/usr/local/bin/python`, resolving to Python 3.12.

## 1. Check Docker and AppArmor

```bash
docker --version
docker info --format '{{.ServerVersion}}'
docker info --format '{{json .SecurityOptions}}'
command -v apparmor_parser
cat /sys/module/apparmor/parameters/enabled
```

Captured output:

```text
Docker version 29.8.0, build 88096ef
29.8.0
SecurityOptions=["name=apparmor,profile=default","name=seccomp,profile=builtin","name=cgroupns"]
/usr/sbin/apparmor_parser
Y
```

This confirms that the kernel module and parser are present. It does not by itself guarantee that a custom profile can be loaded or attached by this Docker daemon.

## 2. Build the Flask Image

From this directory:

```bash
docker build -t flask-apparmor .
docker images --filter reference=flask-apparmor
```

The image build completed successfully. The final build output included:

```text
 naming to docker.io/library/flask-apparmor:latest
```

Captured local image:

```text
IMAGE flask-apparmor:latest 8cc7509dba1f 204MB
```

## 3. Validate the AppArmor Profile

The profile syntax was checked without changing the host's loaded policy:

```bash
apparmor_parser --skip-kernel-load --skip-read-cache -T ./my-apparmor-profile
```

Captured result: exit code `0`, no parser errors.

**Host administrator step:** loading a policy changes host security state and requires administrator privileges. This session did not run `sudo` or change `/etc/apparmor.d`. To load the profile on a host with AppArmor profile enforcement available:

```bash
sudo install -m 0644 ./my-apparmor-profile /etc/apparmor.d/my-apparmor-profile
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
sudo aa-status | grep -F my-apparmor-profile
```

The Docker security option and SDK scripts use the profile name `my-apparmor-profile`.

## 4. Verify the Flask Container Without the Custom Profile

The app was started without the requested custom profile to verify its HTTP behavior independently:

```bash
docker run -d --name apparmor-baseline -p 5000:5000 flask-apparmor
curl -fsS http://localhost:5000/
docker inspect --format 'Default profile={{.AppArmorProfile}} Security options={{json .HostConfig.SecurityOpt}}' apparmor-baseline
```

Captured evidence:

```text
Container ID: bc89f90fe8a9
Hello, this is a secure Flask application running inside a Docker container!
Default profile=docker-default Security options=null
```

The first HTTP probe ran during container startup and received a connection reset. The subsequent probe succeeded; the container logs showed Flask listening on `0.0.0.0:5000`.

## 5. Apply the Custom Profile with Docker SDK

Create a local virtual environment and install the pinned requirements, then run the script:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python apply_apparmor.py
```

The Flask image built and the SDK attempted to start a container with `apparmor=my-apparmor-profile`. **This step could not complete in the captured environment.** Docker returned HTTP 400 while attaching the custom policy:

```text
unable to apply apparmor profile: apparmor failed to apply profile:
write fsmount:fscontext:proc/thread-self/attr/apparmor/exec:
no such file or directory
```

The script exited with code `1` and removed its failed-start container. The custom profile therefore was not applied or verified here. The host's existing `docker-default` profile is not evidence that the custom profile works.

After the administrator load step above, rerun the script. On success it prints the HTTP response and `AppArmor profile applied: ['apparmor=my-apparmor-profile']`, then stops and removes the container.

## 6. Test Restricted Actions

After successfully loading the profile and completing Step 5, run:

```bash
.venv/bin/python test_restricted_actions.py
```

This test tries to read `/etc/passwd` with Python and execute `/bin/bash`. It treats either action succeeding as a test failure and removes its container. **The restricted-action checks were not run under the custom profile in this environment** because Docker rejected the profile attachment in Step 5. Do not report the expected denials below as captured results; exit behavior can vary with kernel and Docker versions.

Expected when the policy is successfully enforced:

```text
Attempt to read /etc/passwd: Exit Code non-zero
Attempt to execute /bin/bash: Exit Code non-zero
Both restricted actions were denied
Container stopped and removed
```

## 7. Cleanup

The baseline container used for the successful HTTP check was stopped and removed:

```bash
docker stop apparmor-baseline
docker rm apparmor-baseline
```

Captured cleanup output:

```text
apparmor-baseline
apparmor-baseline
```

The built `flask-apparmor` image and the local Python virtual environment are left in place for rerunning the exercise. Remove them manually when no longer needed:

```bash
docker rmi flask-apparmor
rm -rf .venv
```

Do not unload a host AppArmor profile while a container still depends on it.

## Questions and Answers

1. **Why use AppArmor with Docker?** AppArmor adds mandatory access-control rules that constrain what a process can read, write, execute, and access, beyond ordinary container isolation.
2. **How do profiles secure a container?** A loaded profile is attached to the container process and its descendants; allowed operations proceed and denied operations are blocked and may be logged by the kernel.
3. **Why restrict `/etc` and `/var`?** These locations can contain credentials, host/container configuration, logs, and mutable system state. Restrict only what the application does not need, since overly broad denials can prevent it from starting.
4. **What else can AppArmor restrict?** File access, executable transitions, network families, capabilities such as `sys_admin`, and other mediated operations supported by the host kernel.
5. **How can the applied profile be verified?** Inspect `HostConfig.SecurityOpt` through Docker's inspect API (as `apply_apparmor.py` does), and verify the profile is loaded with `aa-status`. A successful container start alone is not sufficient evidence of the intended policy.

## Result

The Flask image, HTTP endpoint, policy syntax, and Docker SDK code were validated. The custom-profile attachment and denied-operation demonstrations remain host-blocked: the Docker daemon could not attach the custom profile, and this session did not have permission to load or inspect host AppArmor policy. Complete the administrator load step and rerun Steps 5 and 6 to produce successful enforcement evidence.