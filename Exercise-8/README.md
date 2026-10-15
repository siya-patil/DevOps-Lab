# Exercise 8: Hello World Jenkins Job

## Objective

Create a shell script and configure a Jenkins Freestyle project to fetch this repository, run the script, and show `Hello, Jenkins!` in the build console output.

## Files

- [hello-world.sh](hello-world.sh): executable build script.

## 1. Verify the Script Locally

From the repository root:

```bash
chmod +x Exercise-8/hello-world.sh
./Exercise-8/hello-world.sh
```

Captured output:

```text
Hello, Jenkins!
```

## 2. Verify the Jenkins and Git Prerequisites

Jenkins from Exercise 7 is available at [http://localhost:8080](http://localhost:8080), with ports bound only to localhost:

```text
Container: jenkins-exercise-7
Status: running
Ports: 127.0.0.1:8080->8080/tcp, 127.0.0.1:50000->50000/tcp
```

The repository's configured Git remote is:

```text
https://github.com/siya-patil/DevOps-Lab.git
Branch: master
Remote HEAD: c46e0959e431b42ed4688bb8c5022e5a1557fd2d
```

The remote was readable without credentials (`git ls-remote` succeeded). After signing into Jenkins as `admin`, I installed the missing Git plugin and restarted Jenkins so its Freestyle SCM form could load.

Captured Jenkins API check before sign-in:

```text
HTTP 403
Redirect: /login
```

After sign-in, Jenkins displayed the admin dashboard and allowed job configuration. I created and saved the `HelloWorld` Freestyle job with Git SCM and an Execute shell build step. The GitHub URL was then checked for `Exercise-8/hello-world.sh` and returned HTTP 404, so the script has not yet been pushed to the branch Jenkins will build. I have not triggered a build that cannot check out the script.

Captured job configuration:

```text
Job: HelloWorld
Type: Freestyle project
Source Code Management: Git
Repository URL: https://github.com/siya-patil/DevOps-Lab.git
Branch specifier: */master
Build step: Execute shell
cd Exercise-8
chmod +x hello-world.sh
./hello-world.sh
Build history: No builds (waiting for hello-world.sh to be pushed)
```

## 3. Create the Freestyle Job in Jenkins

The `HelloWorld` job is already configured in the running Jenkins instance. First push `Exercise-8/hello-world.sh` to the `master` branch of the configured repository. Then:

1. Open [HelloWorld in Jenkins](http://localhost:8080/job/HelloWorld/).
2. Select **Build Now**.
3. Open the build number under **Build History**, then choose **Console Output**.

Expected successful Jenkins console lines:

```text
[HelloWorld] $ /bin/sh -xe /tmp/jenkins-build-step.sh
+ cd Exercise-8
+ chmod +x hello-world.sh
+ ./hello-world.sh
Hello, Jenkins!
Finished: SUCCESS
```

These are the expected lines, not yet captured Jenkins output. After the first authenticated build runs, replace this block with the actual Console Output if you need completed Jenkins execution evidence in this README.

## Result

The script has been created, made executable, and run locally with the expected output. The authenticated Jenkins Freestyle job is configured and saved. Jenkins build execution remains pending until the script is pushed to the configured GitHub branch. No credentials or personal access tokens are stored in this project.