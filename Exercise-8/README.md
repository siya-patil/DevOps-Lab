# Exercise 8: Hello World Jenkins Job

## Objective

Create a shell script, push it to GitHub, and run it from a Jenkins Freestyle job.

## Files

- [hello-world.sh](hello-world.sh): executable build script.

## 1. Verify the Script

```bash
./Exercise-8/hello-world.sh
```

Captured output:

```text
Hello, Jenkins!
```

## 2. Push the Script to GitHub

Repository and branch used by Jenkins:

```text
https://github.com/siya-patil/DevOps-Lab.git
master
```

The script is present at `Exercise-8/hello-world.sh` in commit `4a921ad5e1e35be4eacf457df619ff134553db4f`.

## 3. Configure the Jenkins Freestyle Job

The `HelloWorld` job is configured at [http://localhost:8080/job/HelloWorld](http://localhost:8080/job/HelloWorld):

```text
Type: Freestyle project
Source Code Management: Git
Repository URL: https://github.com/siya-patil/DevOps-Lab.git
Branch specifier: */master
Build step: Execute shell
cd Exercise-8
chmod +x hello-world.sh
./hello-world.sh
```

## 4. Run and Verify the Job

Jenkins build `#1` completed successfully in `4.8 sec`.

Captured Console Output:

```text
Started by user admin
Building in workspace /var/jenkins_home/workspace/HelloWorld
Cloning repository https://github.com/siya-patil/DevOps-Lab.git
Checking out Revision 4a921ad5e1e35be4eacf457df619ff134553db4f (refs/remotes/origin/master)
Commit message: "Exercise-8: pushing file for jenkins build"
[HelloWorld] $ /bin/sh -xe /tmp/jenkins4488870682285023006.sh
+ cd Exercise-8
+ chmod +x hello-world.sh
+ ./hello-world.sh
Hello, Jenkins!
Finished: SUCCESS
```

Open the [Jenkins build console](http://localhost:8080/job/HelloWorld/1/console) to view the build output.

## Result

The local script and Git-backed Jenkins job both printed `Hello, Jenkins!`. The Jenkins build completed with `SUCCESS`.