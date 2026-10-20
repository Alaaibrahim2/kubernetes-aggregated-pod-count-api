from collections import Counter

from fastapi import FastAPI, HTTPException
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

app = FastAPI()

GROUP = "demo.example.com"
VERSION = "v1"

# Inside Kubernetes, use the Pod's ServiceAccount.
# For local development, fall back to kubeconfig.
try:
    config.load_incluster_config()
except ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()


@app.get(f"/apis/{GROUP}")
def api_group():
    return {
        "kind": "APIGroup",
        "apiVersion": "v1",
        "name": GROUP,
        "versions": [
            {
                "groupVersion": f"{GROUP}/{VERSION}",
                "version": VERSION,
            }
        ],
        "preferredVersion": {
            "groupVersion": f"{GROUP}/{VERSION}",
            "version": VERSION,
        },
    }


@app.get(f"/apis/{GROUP}/{VERSION}")
def api_resources():
    return {
        "kind": "APIResourceList",
        "apiVersion": "v1",
        "groupVersion": f"{GROUP}/{VERSION}",
        "resources": [
            {
                "name": "namespaces",
                "singularName": "namespace",
                "namespaced": False,
                "kind": "NamespacePodCount",
                "verbs": ["get"],
            }
        ],
    }


@app.get(f"/apis/{GROUP}/{VERSION}/namespaces")
def count_pods():
    try:
        namespaces = v1.list_namespace().items
        pods = v1.list_pod_for_all_namespaces().items

        counts = Counter(
            pod.metadata.namespace
            for pod in pods
        )

        return {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "NamespacePodCountList",
            "items": [
                {
                    "namespace": ns.metadata.name,
                    "podCount": counts[ns.metadata.name],
                }
                for ns in namespaces
            ],
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pod counts from Kubernetes",
        )
