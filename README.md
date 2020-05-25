# Welcome to TheDemoDrive

This is the guideline to set up Istio with KeyfactorCA

## Resources

- Build Instructions: [Link](https://github.com/thedemodrive/examples/blob/master/BUILD.md)
- Code repository: [https://github.com/thedemodrive/istio](https://github.com/thedemodrive/istio)
- Docker images: [https://hub.docker.com/orgs/thedemodrive/repositories](https://hub.docker.com/orgs/thedemodrive/repositories)

## Prerequisite

- These steps require you to have a cluster running a compatible version of Kubernetes. You can use any supported platform, for example [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) or others specified by the [platform-specific setup instructions](https://istio.io/docs/setup/platform-setup/).
- Add the  `istioctl`  client to your path (Linux or macOS or Windows):
  - OSX at: `./release/istioctl-osx`
  - Linux at: `./release/istioctl-linux-amd64`
  - Windows at: `./release/istioctl-win.exe`
- Create a file `./root-cert.pem` contains root certificate from Keyfactor

## Create root certificate

Create kubernetes secrets with the root-cert (Istiod need root cert to handshake mTLS with IstioAgents)

```bash
kubectl create namespace istio-system
kubectl create secret generic cacerts -n istio-system --from-file=./root-cert.pem
```

> file: ./root-cert.pem is CA pem of KeyfactorCA

## OPTION 1: Setup KeyfactorCA Istio with Kubernetes Secret

1. Create secret `example-keyfactor-secret` to contains Credentials Keyfactor

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: keyfactor-secret-example
  namespace: istio-system
type: Opaque
stringData:
  # Name of certificate authorization
  caName: ""

  # Using for authentication header
  authToken: ""

  # Certificate Template for enroll the new one: Default is Istio
  caTemplate: "Istio"

  # ApiKey from Api Setting
  appKey: "gf4CHE6R0shrDg=="
  
```

2. Update the Keyfactor configuration at `./keyfactor-with-secret.yaml`

```yaml
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: keyfactor-with-secret
spec:
  profile: demo
  values:
    global:
      hub: thedemodrive
      tag: final-01
      imagePullPolicy: "Always"
      multiCluster:
        clusterName: FinalBuildCluster
      controlPlaneSecurityEnabled: true
      caProvider: "KeyfactorCA"
      caAddress: "https://kmstech.thedemodrive.com"
      # Configure the external CA Provider by Keyfactor.
      keyfactor:
        #####
        # SecretName name of secret contain Keyfactor Credentials
        # Let empty for using yaml config
        # Each namespace must have one secret (pod only ready secret within namespace)
        secretName: "keyfactor-secret-example"
        ######
        # Customize metadata fields to carry with CSR enroll certificates
        # Remove from list if you dont need
        # Only support for: Cluster, Service, PodName, PodNameSpace, PodIP, TrustDomain.
        metadata:
          - name: Cluster # Do not modified it
            alias: Cluster # Name of custom metadata field on Keyfactor Platform
          - name: Service
            alias: Service
          # - name: PodName
          #   alias: PodName
          # - name: PodNamespace
          #   alias: PodNamespace
          # - name: PodIP
          #   alias: PodIP
          # - name: TrustDomain
          #   alias: TrustDomain

```

3. Install with **Istioctl**

    ```bash
    istioctl manifest --set installPackagePath=installs apply -f ./keyfactor-with-secret.yaml
    ```

## OPTION 2: Setup KeyfactorCA Istio with YAML Config

1. Update the Keyfactor configuration at `./keyfactor-config.yaml`

```yaml
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: keyfactor-yaml-config
spec:
  profile: demo
  values:
    global:
      hub: thedemodrive
      tag: final-01
      imagePullPolicy: "Always"
      multiCluster:
        clusterName: FinalBuildCluster
      controlPlaneSecurityEnabled: true
      caProvider: "KeyfactorCA"
      caAddress: "https://kmstech.thedemodrive.com"
      # Configure the external CA Provider by Keyfactor.
      keyfactor:
        ########
        # SecretName name of secret contain Keyfactor Credentials
        # Let empty for using yaml config
        # Each namespace must have one secret (pod only ready secret within namespace)
        secretName: ""
        # Name of certificate authorization
        caName: ""
        # Using for authentication header
        authToken: ""
        # ApiKey from Api Setting
        appKey: ""
        # Name of Keyfactor template
        caTemplate: "Istio"
        ########
        # Custom metadata fields attached to CSR request CSR enroll certificates
        # Remove from list if you dont need
        # Only support for: Cluster, Service, PodName, PodNameSpace, PodIP, TrustDomain.
        metadata:
          - name: Cluster # Do not modified it
            alias: Cluster # Name of custom metadata field on Keyfactor Platform
          - name: Service
            alias: Service
          # - name: PodName
          #   alias: PodName
          # - name: PodNamespace
          #   alias: PodNamespace
          # - name: PodIP
          #   alias: PodIP
          # - name: TrustDomain
          #   alias: TrustDomain

```

2. Install with **Istioctl**

    ```bash
    istioctl manifest --set installPackagePath=installs apply -f ./keyfactor-config.yaml
    ```

## Setup example Microservices

Deploy Book-Info microservice example of Istio ([references](https://istio.io/docs/examples/bookinfo/))
  ![Book Info Sample](https://istio.io/docs/examples/bookinfo/withistio.svg)

- Turn on Istio auto-inject for namespace **default**

   ``` bash
   kubectl label namespace default istio-injection=enabled
   ```

- Deploy an example of istio ([Book-Info](https://istio.io/docs/examples/bookinfo/))

   ``` bash
   kubectl apply -f ./samples/bookinfo/platform/kube/bookinfo.yaml
   ```

- Configure a gateway for the Book-Info sample

   ``` bash
   kubectl apply -f ./samples/bookinfo/networking/bookinfo-gateway.yaml
   ```

- Configure mTLS destination rules

   ``` bash
   kubectl apply -f ./samples/bookinfo/networking/destination-rule-all-mtls.yaml
   ```

- Lock down mutual TLS for the entire mesh

   ``` bash
   kubectl apply -f ./samples/peer-authentication.yaml
   ```

## HOW TO VERIFY THE TRAFFIC IS USING MUTUAL TLS ENCRYPTION

Lock down mutual TLS for the entire mesh

``` bash
kubectl apply -f ./samples/peer-authentication.yaml
```

### Create the namespace "insidemesh" and deploy a sleep container **with sidecars**

```bash
kubectl create ns insidemesh
kubectl label namespace insidemesh istio-injection=enabled
kubectl apply -f ./samples/sleep/sleep.yaml -n insidemesh
```

Verify the setup by sending an http request (using curl command) from sleep pod (namespace: insidemesh) to productpage.default:9080:

1. To check if the certificate get from productpage.default is issued by KeyfactorCA

```bash
kubectl exec $(kubectl get pod -l app=sleep -n insidemesh -o jsonpath={.items..metadata.name}) -c sleep -n insidemesh -- openssl s_client -showcerts -connect productpage.default:9080
```

2. Request using curl

```bash
kubectl exec $(kubectl get pod -l app=sleep -n insidemesh -o jsonpath={.items..metadata.name}) -c sleep -n insidemesh -- curl http://productpage.default:9080 -s -o /dev/null -w "sleep.insidemesh to http://productpage.default:9080: -> HTTP_STATUS: %{http_code}\n"
```

> Note: every workload **deployed with sidecar** can access Book Info services (HTTP_STATUS = 200)

### Create another namespace "outsidemesh" and deploy a sleep container **without a sidecar**

```bash
kubectl create ns outsidemesh
kubectl apply -f samples/sleep/sleep.yaml -n outsidemesh
```

Verify the setup by sending an http request (using curl command) from sleep pod (namespace: outsidemesh) to productpage.default:9080:

```bash
kubectl exec $(kubectl get pod -l app=sleep -n outsidemesh -o jsonpath={.items..metadata.name}) -c sleep -n outsidemesh -- curl http://productpage.default:9080 -s -o /dev/null -w "sleep.outsidemesh to http://productpage.default:9080: -> HTTP_STATUS: %{http_code}\n"
```

> Note: every workload **deployed without sidecar** cannot access Book Info services (HTTP_STATUS = 000)
