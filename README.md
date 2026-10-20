# Kubernetes Aggregated Pod Count API

A custom Kubernetes Aggregated API Server built with Python and FastAPI that exposes the number of Pods in each Kubernetes Namespace through the Kubernetes Aggregation Layer.

## Overview

This project demonstrates how to extend the Kubernetes API using the Aggregation Layer. A custom API server retrieves Namespace and Pod information from the Kubernetes cluster and exposes a custom API endpoint that returns the Pod count for every Namespace.

Instead of querying the built-in Kubernetes API directly from `kubectl`, users can access the custom API through the Kubernetes API Server.

## Architecture

```text
                 kubectl
                    |
                    v
        Kubernetes API Server
                    |
                    v
           Aggregation Layer
                    |
              APIService
                    |
                    v
            Kubernetes Service
                    |
                    v
           Python API Server
            FastAPI + Uvicorn
                    |
                    v
          Kubernetes Python Client
                    |
                    v
          Kubernetes API Resources
             /             \
        Namespaces         Pods
                    |
                    v
       Pod Count per Namespace
```

## Features

- Custom Kubernetes API Group: `demo.example.com`
- API version: `v1`
- Namespace-level Pod counting
- Kubernetes Aggregation Layer integration using `APIService`
- HTTPS communication using TLS certificates
- Kubernetes ServiceAccount and RBAC for API access
- Containerized application using Docker
- Deployment inside a Kubernetes cluster

## Technology Stack

- Kubernetes
- Kubernetes Aggregation Layer
- Python
- FastAPI
- Uvicorn
- Kubernetes Python Client
- Docker
- TLS / HTTPS
- Kubernetes RBAC

## API Endpoint

The custom API is exposed through the Kubernetes API Server:

```text
/apis/demo.example.com/v1/namespaces
```

### Example Request

```bash
kubectl get --raw "/apis/demo.example.com/v1/namespaces"
```

### Example Response

```json
{
  "apiVersion": "demo.example.com/v1",
  "kind": "NamespacePodCountList",
  "items": [
    {
      "namespace": "default",
      "podCount": 4
    },
    {
      "namespace": "argocd",
      "podCount": 8
    },
    {
      "namespace": "kube-system",
      "podCount": 21
    }
  ]
}
```

*The values above are illustrative. Actual counts depend on the current cluster state.*

## Project Structure

```text
kubernetes-aggregated-pod-count-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── rbac.yaml
├── deployment.yaml
├── apiservice.yaml
└── certs/
    ├── ca.crt
    ├── server.crt
    └── server.key
```

**Security note:** Do not commit private keys, access tokens, or other secrets to Git. Keep generated private keys such as `ca.key` and `server.key` out of the repository. The `certs/` directory above illustrates the local certificate files used during development; the Kubernetes TLS Secret should provide the server certificate and key to the running application.

## How It Works

1. The Kubernetes API Server receives a request for the custom API group.
2. The Aggregation Layer checks the registered `APIService`.
3. The request is routed to the `pod-count-api` Kubernetes Service.
4. The FastAPI application queries Namespaces and Pods through the Kubernetes Python Client.
5. The application counts Pods by Namespace and returns a JSON response.

## Security

### TLS

The custom API server uses HTTPS. Its server certificate is signed by a Certificate Authority (CA), and the CA certificate is configured in the `APIService` resource so that the Kubernetes API Server can validate the backend server certificate.

### RBAC

A dedicated Kubernetes ServiceAccount is used by the application. Its ClusterRole grants permission to list Pods and Namespaces, which are the resources required to calculate the counts.

## Deployment

The deployment process includes:

1. Generate a TLS certificate and key.
2. Create the Kubernetes TLS Secret.
3. Build and publish the Docker image to a container registry.
4. Apply the RBAC configuration.
5. Deploy the application and create its Kubernetes Service.
6. Register the custom API using the `APIService` resource.
7. Test the custom API through `kubectl`.

Apply the Kubernetes resources in the appropriate order:

```bash
kubectl apply -f rbac.yaml
kubectl apply -f deployment.yaml
kubectl apply -f apiservice.yaml
```

Ensure the application image is available to the cluster and that the TLS Secret and CA bundle are configured correctly before registering the API.

## Validation

Check the APIService status:

```bash
kubectl get apiservice v1.demo.example.com
```

Check API discovery:

```bash
kubectl get --raw "/apis/demo.example.com"
kubectl get --raw "/apis/demo.example.com/v1"
```

Retrieve Pod counts:

```bash
kubectl get --raw "/apis/demo.example.com/v1/namespaces"
```

The APIService should report `Available=True` when discovery and backend connectivity are working correctly.

## Learning Outcomes

This project provides hands-on experience with:

- Extending the Kubernetes API using the Aggregation Layer
- Registering custom API groups and versions
- Implementing a REST API with FastAPI
- Querying Kubernetes resources programmatically
- Configuring TLS between Kubernetes components
- Applying least-privilege RBAC
- Deploying containerized applications in Kubernetes
- Troubleshooting APIService availability and backend connectivity

## Future Improvements

- Implement delegated authentication and authorization for full aggregated API server compatibility.
- Add automated tests and health checks.
- Add structured logging and Prometheus metrics.
- Package the deployment using Helm.
- Add CI/CD automation for image builds and deployments.

## Disclaimer

This project is an educational implementation intended to demonstrate Kubernetes API aggregation concepts. Additional authentication, authorization, validation, and operational hardening are required before using it in production.
