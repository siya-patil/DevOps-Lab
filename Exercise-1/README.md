# Exercise 1: Hello Pod

## Objective

Deploy an Nginx container as a Kubernetes Pod using Minikube and expose it through a NodePort Service.

## Prerequisites

* Ubuntu 26.04 LTS
* Docker
* Minikube
* kubectl

## Step 1: Start a Local Kubernetes Cluster with Minikube

### Command

```bash
minikube start
```

### Output

```text
😄  minikube v1.39.0 on Ubuntu 26.04
✨  Using the docker driver based on existing profile
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.51 ...
🔄  Restarting existing docker container for "minikube" ...
📦  Preparing Kubernetes v1.37.0 on containerd 2.3.4 ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass

❗  /usr/bin/kubectl is version 1.34.11, which may have incompatibilities with Kubernetes 1.37.0.
    ▪ Want kubectl v1.37.0? Try 'minikube kubectl -- get pods -A'
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

### Verification

```bash
minikube status
```

Output:

```text
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

The Minikube Kubernetes cluster is running successfully.

## Step 2: Create the First Pod Using the Nginx Image

### Command

```bash
kubectl run hello-k8s --image=nginx --port=80
```

### Output

```text
pod/hello-k8s created
```

A Pod named `hello-k8s` was created using the `nginx` container image.

## Step 3: Verify the Pod

### Command

```bash
kubectl get pods
```

### Initial Output

```text
NAME        READY   STATUS              RESTARTS   AGE
hello-k8s   0/1     ContainerCreating   0          5s
```

The Pod initially entered the `ContainerCreating` state while Kubernetes prepared the Nginx container.

### Final Verification

```bash
kubectl get pods
```

Output:

```text
NAME        READY   STATUS    RESTARTS   AGE
hello-k8s   1/1     Running   0          2m19s
```

The Pod reached the `Running` state successfully.

## Step 4: Expose the Pod as a Service

### Command

```bash
kubectl expose pod hello-k8s --type=NodePort --port=80
```

### Output

```text
service/hello-k8s exposed
```

The `hello-k8s` Pod was successfully exposed through a Kubernetes NodePort Service.

## Step 5: Open the Application

### Command

```bash
minikube service hello-k8s
```

### Output

```text
┌───────────┬───────────┬─────────────┬───────────────────────────┐
│ NAMESPACE │   NAME    │ TARGET PORT │            URL            │
├───────────┼───────────┼─────────────┼───────────────────────────┤
│ default   │ hello-k8s │ 80          │ http://192.168.49.2:31601 │
└───────────┴───────────┴─────────────┴───────────────────────────┘
🎉  Opening service default/hello-k8s in default browser...
```

The Nginx welcome page was successfully opened in the browser.

> Note: The GTK message displayed after opening the browser was a desktop environment message and did not affect the Kubernetes service or application.

## Final Verification

### Command

```bash
kubectl get pods
```

### Output

```text
NAME        READY   STATUS    RESTARTS   AGE
hello-k8s   1/1     Running   0          2m19s
```

## Result

The Nginx application was successfully deployed as a Kubernetes Pod on a local Minikube cluster and exposed through a NodePort Service.

The application was successfully accessed through the Minikube service.
