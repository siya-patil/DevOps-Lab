# Exercise 3: Scale a Flask App with a ReplicaSet

## Objective

Deploy a flash-sale Flask application to a single-node Minikube cluster, run it as three replicas, scale it to five, and observe how Kubernetes replaces a deleted Pod.

## Prerequisites

- Docker
- Minikube
- kubectl
- curl

The files for this exercise are `app.py`, `Dockerfile`, and `flashsale-replicaset.yaml` in this directory. The Flask app listens on port `5000`; the Kubernetes Service exposes it on port `80`.

## Execution Evidence

The following commands were run on 2026-10-01 against the local Minikube profile. The application was built, deployed, exercised through its Service, scaled, and observed replacing a deleted Pod. The final ReplicaSet is intentionally left running at five replicas. Ages and timestamps below reflect the time each command was run.

## Step 1: Start a Single-Node Minikube Cluster

From the repository root, run:

```bash
minikube start --nodes=1
```

Captured output (Minikube v1.39.0, Kubernetes v1.37.0):

```text
😄  minikube v1.39.0 on Ubuntu 26.04
✨  Using the docker driver based on existing profile
❗  You cannot change the number of nodes for an existing minikube cluster. Please use 'minikube node add' to add nodes to an existing cluster.
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🔄  Restarting existing docker container for "minikube" ...
📦  Preparing Kubernetes v1.37.0 on containerd 2.3.4 ...
🔎  Verifying Kubernetes components...
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Verify that the cluster has one ready node:

```bash
kubectl get nodes
```

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   13d   v1.37.0
```

If you already have a cluster, you can use it instead. `minikube delete` is destructive and is not required for this exercise.

## Step 2: Build the Flash-Sale Image

Build the image directly into Minikube's image store so the cluster can run it without pulling it from a registry:

```bash
cd Exercise-3
minikube image build -t flashsale:1.0 .
```

Captured build output excerpt:

```text
#7 Successfully installed Flask-3.1.3 blinker-1.9.0 click-8.5.0 gunicorn-26.2.0 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 werkzeug-3.1.9
#9 naming to docker.io/library/flashsale:1.0 done
#9 DONE 0.7s
```

The image was built directly in Minikube's image store; no registry push was needed.

Optionally, build and publish the image to Docker Hub when you need to use it outside this local cluster:

```bash
docker build -t <dockerhub-username>/flashsale:1.0 .
docker push <dockerhub-username>/flashsale:1.0
```

For a registry deployment, update the image in `flashsale-replicaset.yaml` to `<dockerhub-username>/flashsale:1.0` before applying it.

## Step 3: Apply the ReplicaSet and Service

The manifest creates three Pods and a ClusterIP Service named `flashsale-svc`:

```bash
kubectl apply -f flashsale-replicaset.yaml
```

Captured output:

```text
replicaset.apps/flashsale-rs created
service/flashsale-svc created
```

Wait for all three replicas to become ready:

```bash
kubectl wait --for=condition=Ready pod -l app=flashsale --timeout=120s
```

```text
pod/flashsale-rs-4gln9 condition met
pod/flashsale-rs-kj8wl condition met
pod/flashsale-rs-rdfs6 condition met
```

Check the ReplicaSet:

```bash
kubectl get rs
```

```text
NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   3         3         3       11s
```

Check the Pods:

```bash
kubectl get pods -l app=flashsale
```

```text
NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-4gln9   1/1     Running   0          11s
flashsale-rs-kj8wl   1/1     Running   0          11s
flashsale-rs-rdfs6   1/1     Running   0          11s
```

## Step 4: Access the Application and Observe Requests

The Service is internal to the cluster. Start a temporary curl client Pod:

```bash
kubectl run flashsale-client --image=curlimages/curl:8.12.1 --restart=Never --command -- sleep 3600
kubectl wait --for=condition=Ready pod/flashsale-client --timeout=120s
```

Captured output:

```text
pod/flashsale-client created
pod/flashsale-client condition met
```

Call the homepage, purchase endpoint, and health endpoint through the Service:

```bash
kubectl exec flashsale-client -- curl -s http://flashsale-svc/
kubectl exec flashsale-client -- curl -s 'http://flashsale-svc/buy?user=123'
kubectl exec flashsale-client -- curl -s http://flashsale-svc/health
```

Captured responses (the hostname is the Pod that served that request):

```json
{"message":"Welcome to Big Sale!","pod":"flashsale-rs-4gln9","ts":1790835020.7391682}
{"item":"Laptop","served_by_pod":"flashsale-rs-4gln9","status":"success","time":"06:10:20","user":"123"}
{"pod":"flashsale-rs-4gln9","status":"healthy"}
```

Send several separate requests to see which replicas answer. Service routing is not guaranteed to distribute a small sample evenly:

```bash
kubectl exec flashsale-client -- sh -c 'for i in $(seq 1 9); do curl -s "http://flashsale-svc/buy?user=$i"; echo; done'
```

Captured output (look at `served_by_pod`; all three initial replicas served requests):

```text
{"item":"Laptop","served_by_pod":"flashsale-rs-rdfs6","status":"success","time":"06:10:21","user":"1"}
{"item":"Shoes","served_by_pod":"flashsale-rs-kj8wl","status":"success","time":"06:10:21","user":"2"}
{"item":"Headphones","served_by_pod":"flashsale-rs-kj8wl","status":"success","time":"06:10:21","user":"3"}
{"item":"Shoes","served_by_pod":"flashsale-rs-kj8wl","status":"success","time":"06:10:21","user":"4"}
{"item":"Laptop","served_by_pod":"flashsale-rs-rdfs6","status":"success","time":"06:10:21","user":"5"}
{"item":"Smartphone","served_by_pod":"flashsale-rs-rdfs6","status":"success","time":"06:10:21","user":"6"}
{"item":"Headphones","served_by_pod":"flashsale-rs-4gln9","status":"success","time":"06:10:21","user":"7"}
{"item":"Shoes","served_by_pod":"flashsale-rs-kj8wl","status":"success","time":"06:10:21","user":"8"}
{"item":"Laptop","served_by_pod":"flashsale-rs-kj8wl","status":"success","time":"06:10:21","user":"9"}
```

## Step 5: Scale the ReplicaSet to Five

```bash
kubectl scale rs flashsale-rs --replicas=5
```

```text
replicaset.apps/flashsale-rs scaled
```

Wait for all five replicas:

```bash
kubectl wait --for=condition=Ready pod -l app=flashsale --timeout=120s
kubectl get rs
```

Relevant captured output:

```text
NAME          DESIRED   CURRENT   READY   AGE
flashsale-rs  5         5         5       41s
```

Verify the five Pods:

```bash
kubectl get pods -l app=flashsale
```

```text
NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-24gqw   1/1     Running   0          6s
flashsale-rs-4gln9   1/1     Running   0          41s
flashsale-rs-7rvfd   1/1     Running   0          6s
flashsale-rs-kj8wl   1/1     Running   0          41s
flashsale-rs-rdfs6   1/1     Running   0          41s
```

## Step 6: Delete a Pod and Observe Replacement

The captured run deleted `flashsale-rs-4gln9`:

```bash
kubectl delete pod flashsale-rs-4gln9
```

```text
pod "flashsale-rs-4gln9" deleted from default namespace
```

The ReplicaSet creates a replacement to return to five replicas. The replacement has a new generated Pod name:

```bash
kubectl get pods -l app=flashsale
```

```text
NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-24gqw   1/1     Running   0          20s
flashsale-rs-4jvw7   1/1     Running   0          6s
flashsale-rs-7rvfd   1/1     Running   0          20s
flashsale-rs-kj8wl   1/1     Running   0          55s
flashsale-rs-rdfs6   1/1     Running   0          55s
```

## Step 7: View Pod Placement on the Single Node

```bash
kubectl get pods -l app=flashsale -o wide
```

Captured output after Pod replacement:

```text
NAME                 READY   STATUS    RESTARTS   AGE    IP            NODE
flashsale-rs-24gqw   1/1     Running   0          20s    10.244.0.8    minikube
flashsale-rs-4jvw7   1/1     Running   0          6s     10.244.0.10   minikube
flashsale-rs-7rvfd   1/1     Running   0          20s    10.244.0.9    minikube
flashsale-rs-kj8wl   1/1     Running   0          55s    10.244.0.6    minikube
flashsale-rs-rdfs6   1/1     Running   0          55s    10.244.0.4    minikube
```

All five Pods are scheduled on the single `minikube` node. The Service selects Pods by the shared `app: flashsale` label.

## Step 8: Inspect Resources and Logs

Describe the ReplicaSet:

```bash
kubectl describe rs flashsale-rs
```

Captured output:

```text
Name:         flashsale-rs
Namespace:    default
Selector:     app=flashsale
Replicas:     5 current / 5 desired
Pods Status:  5 Running / 0 Waiting / 0 Succeeded / 0 Failed
Image:        flashsale:1.0
Port:         5000/TCP (http)
Liveness:     http-get http://:http/health delay=10s timeout=1s period=10s
Readiness:    http-get http://:http/health delay=2s timeout=1s period=5s
Events:
	Normal  SuccessfulCreate  Created pod: flashsale-rs-rdfs6
	Normal  SuccessfulCreate  Created pod: flashsale-rs-kj8wl
	Normal  SuccessfulCreate  Created pod: flashsale-rs-4gln9
	Normal  SuccessfulCreate  Created pod: flashsale-rs-24gqw
	Normal  SuccessfulCreate  Created pod: flashsale-rs-7rvfd
	Normal  SuccessfulCreate  Created pod: flashsale-rs-4jvw7
```

Read logs from one application Pod:

```bash
kubectl logs flashsale-rs-24gqw
```

Captured output:

```text
[2026-10-01 06:10:26 +0000] [1] [INFO] Starting gunicorn 26.2.0
[2026-10-01 06:10:26 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
[2026-10-01 06:10:26 +0000] [1] [INFO] Using worker: gthread
[2026-10-01 06:10:26 +0000] [8] [INFO] Booting worker with pid: 8
[2026-10-01 06:10:26 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl
```

The Service was backed by five endpoints:

```text
NAME            ENDPOINTS
flashsale-svc   10.244.0.10:5000,10.244.0.4:5000,10.244.0.6:5000 + 2 more...
```

## Optional Cleanup

Cleanup was not run after evidence collection; the ReplicaSet and Service are left deployed so the final state can be inspected. To remove them after grading:

Delete the ReplicaSet, Service, and temporary client Pod:

```bash
kubectl delete -f flashsale-replicaset.yaml
kubectl delete pod flashsale-client --ignore-not-found
```

This cleanup command was not run as part of the captured exercise.

## Questions and Answers

**1. What is the initial number of replicas in the ReplicaSet?**  
Three, as set by `spec.replicas` in the manifest.

**2. How many application Pods should be running after applying the configuration?**  
Three, once all Pods become ready.

**3. What happens when the ReplicaSet is scaled to five replicas?**  
Kubernetes creates two additional Pods to reach the desired count of five.

**4. What happens when one Pod is deleted?**  
The ReplicaSet notices that only four of the desired five Pods remain and creates a replacement Pod.

**5. How does Kubernetes maintain the desired number of replicas?**  
The ReplicaSet controller continuously compares the number of Pods matching its selector with the desired replica count, creating or removing Pods as needed.

**6. How many nodes are running in this exercise?**  
One Minikube node.

**7. Where do the five Pods run with respect to the nodes?**  
All five Pods run on the single `minikube` node. Replica count increases the number of application Pods, not the number of nodes.

**8. What does the Service do?**  
`flashsale-svc` provides a stable in-cluster address and forwards requests on port `80` to healthy Pods listening on port `5000`.

## Key Learnings

- A ReplicaSet maintains the desired number of matching Pods and replaces deleted Pods.
- Scaling out creates more identical application Pods; it does not add cluster nodes.
- A Service provides a stable endpoint and routes requests to selected Pods.
- Readiness and liveness probes use `/health` to check each container.
- `kubectl get pods -o wide` shows the node and IP for each Pod.

## Additional Challenges

- Change the image tag, rebuild it in Minikube, and update the manifest.
- Create a Deployment instead of a standalone ReplicaSet; a Deployment manages ReplicaSets and is the usual workload controller for applications.
- Use `kubectl describe pod <pod-name>` and compare the Pod events before and after deleting a replica.