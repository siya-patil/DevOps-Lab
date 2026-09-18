# Exercise: Deploy a Flask app on Minikube using kubectl and yaml

## Objective
Learn Kubernetes basics using Minikube to set up a single-node cluster and deploy Python applications. 
This exercise involves deploying a Flask app using minikube.

# Q&A based on the exercise   

**Q1: What is the purpose of minikube service flask-app-service --url?**
A1: To provide the URL for accessing the flask-app-service running in Minikube.

**Q2: What happens when you run minikube service flask-app-service --url?**
A2: Minikube checks if the service is running, generates a URL, and displays it in the terminal.

**Q3: Why is targetPort used in Kubernetes Service configuration?**
A3: To specify the port number on which the container is listening.

**Q4: What is the difference between port and targetPort in Kubernetes Service configuration?**
A4: port is the exposed Service port, while targetPort is the container port.

**Q5: How do you access a Flask application running in Minikube?**
A5: Use minikube service <service-name> --url to get the access URL.

**Q6: Why does the terminal need to remain open when using Docker driver on Linux with Minikube?**
A6: Because the Docker driver requires the terminal to stay open to maintain the Minikube connection.

**Q7: What is the benefit of using --url flag with minikube service command?**
A7: It provides a convenient way to access the service without manually constructing the URL.

**Q8: What command is used to expose a service in Kubernetes?**   
**A8:** kubectl expose or kubectl apply -f <service.yaml> is used to expose a service in Kubernetes.

**Q9: How does Minikube help in local Kubernetes testing?**  
**A9:** Minikube runs a single-node Kubernetes cluster locally, making it easier to test deployments without needing a full Kubernetes environment.

**Q10: What is the role of kubectl in this setup?**
**A10:** kubectl is the Kubernetes CLI tool used to interact with the Kubernetes cluster. It allows you to deploy applications, scale them, and manage resources.

---

# Assignment Completion Evidence

The following outputs were captured from the completed Exercise-2. The cluster used the Docker driver with Minikube v1.39.0 and Kubernetes v1.37.0.

## Step 1: Start Minikube

Command:

```bash
minikube start
```

Output:

```text
minikube v1.39.0 on Ubuntu 26.04
Using the docker driver based on existing profile
Starting "minikube" primary control-plane node
Preparing Kubernetes v1.37.0 on containerd 2.3.4
Verifying Kubernetes components...
Enabled addons: storage-provisioner, default-storageclass
Done! kubectl is now configured to use "minikube" cluster
```

Final status check:

```bash
minikube status
```

```text
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

## Steps 2-3: Flask Application and Dockerfile

The required files are present and match the exercise:

- `app.py` runs Flask on `0.0.0.0:15000` and returns `Hello from Flask on Kubernetes!`.
- `Dockerfile` uses `python:3.8-slim`, installs Flask, and starts `app.py`.

Python syntax verification completed successfully with no output:

```bash
python3 -m py_compile Exercise-2/app.py
```

## Step 4: Build the Docker Image

Command:

```bash
docker build -t flask-app:latest Exercise-2
```

Result:

```text
[+] Building 11.0s (9/9) FINISHED
=> naming to docker.io/library/flask-app:latest
```

The image was then loaded into Minikube:

```bash
minikube image load flask-app:latest
```

Image verification:

```text
flask-app:latest image exists
```

## Step 5: Kubernetes Deployment Manifest

The completed manifest is [flask-deployment.yaml](flask-deployment.yaml). It defines:

- Deployment `flask-app`
- One replica
- Local image `flask-app:latest`
- `imagePullPolicy: Never`
- Container port `15000`
- NodePort Service `flask-app-service`
- Service port and target port both set to `15000`

## Step 6: Deploy the Application

Command:

```bash
kubectl apply -f Exercise-2/flask-deployment.yaml
```

Output:

```text
deployment.apps/flask-app created
service/flask-app-service created
```

Final re-apply verification:

```text
deployment.apps/flask-app unchanged
service/flask-app-service unchanged
```

## Step 7: Check Deployment Status

Command and output:

```bash
kubectl get deployments
```

```text
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
flask-app   1/1     1            1           3m58s
```

Rollout verification:

```bash
kubectl rollout status deployment/flask-app --timeout=30s
```

```text
deployment "flask-app" successfully rolled out
```

## Step 8: Verify the Pod

Command and output:

```bash
kubectl get pods -l app=flask-app
```

```text
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-59f7cdccb4-vd874   1/1     Running   0          3m59s
```

## Step 9: Describe the Deployment

Command:

```bash
kubectl describe deployment flask-app
```

Relevant output:

```text
Name:                   flask-app
Namespace:              default
Selector:               app=flask-app
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
Pod Template:
  Labels:  app=flask-app
  Containers:
   flask-app:
    Image:         flask-app:latest
    Port:          15000/TCP
Conditions:
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
NewReplicaSet:   flask-app-59f7cdccb4 (1/1 replicas created)
Events:
  Normal  ScalingReplicaSet  Scaled up replica set flask-app-59f7cdccb4 from 0 to 1
```

## Step 10: View Deployment Logs

Command:

```bash
kubectl logs deployment/flask-app
```

Output:

```text
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:15000
 * Running on http://10.244.0.3:15000
Press CTRL+C to quit
```

## Step 11: Check the Service

Command and output:

```bash
kubectl get services
```

```text
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
flask-app-service   NodePort    10.103.77.170   <none>        15000:30798/TCP
kubernetes          ClusterIP   10.96.0.1       <none>        443/TCP
```

The Service selected the running pod:

```bash
kubectl get endpoints flask-app-service
```

```text
NAME                ENDPOINTS          AGE
flask-app-service   10.244.0.3:15000   4m2s
```

## Step 12: Test Direct Localhost Access

The exercise intentionally demonstrates that the container port is not automatically exposed on the host. Before creating the Service, the direct request produced:

```bash
curl http://127.0.0.1:15000
```

```text
curl: (7) Failed to connect to 127.0.0.1 port 15000
```

## Step 13: Access the Flask Service

Command and output:

```bash
minikube service flask-app-service --url
```

```text
http://192.168.49.2:30798
```

End-to-end request:

```bash
curl --fail --silent --show-error http://192.168.49.2:30798
```

```text
Hello from Flask on Kubernetes!
```

## Browser Proof

The Service was also opened in a browser and returned the expected response:

![Flask application running through the Minikube NodePort Service](flask-app-screenshot.png)

**Completion result:** The Flask application is containerized, deployed to Minikube, exposed through a Kubernetes NodePort Service, and verified through both `curl` and a browser.
