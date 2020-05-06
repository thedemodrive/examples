# Welcome to TheDemoDrive!

## Resources

- Code repository: [https://github.com/thedemodrive/istio](https://github.com/thedemodrive/istio)
- Pull request for KeyfactorCA Prototype: [https://github.com/thedemodrive/istio/pull/2](https://github.com/thedemodrive/istio/pull/2)
- Public docker hub: [https://hub.docker.com/orgs/thedemodrive/repositories](https://hub.docker.com/orgs/thedemodrive/repositories)

## Prerequisite

- These steps require you to have a cluster running a compatible version of Kubernetes. You can use any supported platform, for example [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) or others specified by the [platform-specific setup instructions](https://istio.io/docs/setup/platform-setup/).
- Add the  `istioctl`  client to your path (Linux or macOS or Windows):
  	- OSX at: `./istio/istioctl-osx`
  	- Linux at: `./istio/istioctl-linux-amd64`
  	- Windows at: `./istio/istioctl-win.exe`
- Create file `./root-cert.pem` contains root certificate from Keyfactor

## How to setup Istio integrate with KeyfactorCA

1. Create kubernetes secrets carry root-cert

```bash
kubectl create namespace istio-system
kubectl create secret generic cacerts -n istio-system --from-file=./root-cert.pem
```

> file: ./root-cert.pem is CA pem of KeyfactorCA

2. Update Keyfactor configuration at `./demo-configuration.yaml`

```yaml
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: example-integrate-keyfactor-ca
spec:
  profile: demo
  values:
    global:
      hub: "thedemodrive" # https://hub.docker.com/orgs/thedemodrive/repositories
      tag: "preview"
      multiCluster:
        # ClusterID, in case multi-cluster is enabled
        clusterName: DemoDriveCluster
      controlPlaneSecurityEnabled: true
      # The variable to config CA Provider of sidecar. Currently supported: KeyfactorCA, GoogleCA, Citadel
      caProvider: ""
      # The endpoint of CA Provider
      caAddress: "" # https://<REPLACE_ME>.thedemodrive.com
      # Configure the external CA Provider by Keyfactor.
      keyfactor:
        # Name of certificate authorization
        ca: ""
        # Using for authentication header
        authToken: ""
        # API path for enroll new certificate from Keyfactor. Default: /KeyfactorAPI/Enrollment/CSR
        enrollPath: ""
        # Certificate Template for enroll the new one: Default: Istio
        caTemplate: ""
        # ApiKey from Api Setting
        appKey: ""

```
 
3. Customizable Install with **Istioctl**

    ```bash
    istioctl manifest --set installPackagePath=charts apply -f ./demo-configuration.yaml
    ```

4. Deploy Book-Info microservice example of Istio ([references](https://istio.io/docs/examples/bookinfo/))
  ![Book Info Sample](https://istio.io/docs/examples/bookinfo/withistio.svg)
   - Turn on Istio auto-inject for namespace **default**

   ``` bash
   kubectl label namespace default istio-injection=enabled
   ```

   - Deploy example of istio ([Book-Info](https://istio.io/docs/examples/bookinfo/))

   ``` bash
   kubectl apply -f ./samples/bookinfo/platform/kube/bookinfo.yaml
   ```

   - Configure gateway for book-info sample

   ``` bash
   kubectl apply -f ./samples/bookinfo/networking/bookinfo-gateway.yaml
   ```

   - Configure mTLS destination rules

   ``` bash
   kubectl apply -f ./samples/bookinfo/networking/destination-rule-all-mtls.yaml
   ```

   - Turn mTLS strictly for all mesh

   ``` bash
   kubectl apply -f ./samples/peer-authentication.yaml
   ```

## HOW CAN I VERIFY THAT TRAFFIC IS USING MUTUAL TLS ENCRYPTION?

Turn mTLS strictly for all namespace default

``` bash
kubectl apply -f ./samples/peer-authentication.yaml
```

### Create namespace insidemesh and deploy sleep **with sidecars**:

```bash
kubectl create ns insidemesh
kubectl label namespace insidemesh istio-injection=enabled
kubectl apply -f ./samples/sleep/sleep.yaml -n insidemesh
```

Verify setup by sending an http request (using curl command) from sleep pod (namespace: insidemesh) to productpage.default:9080:

1. To check certificate from productpage.default is from KeyfactorCA

```bash
kubectl exec $(kubectl get pod -l app=sleep -n insidemesh -o jsonpath={.items..metadata.name}) -c sleep -n insidemesh -- openssl s_client -showcerts -connect productpage.default:9080
```

2. Request by curl

```bash
kubectl exec $(kubectl get pod -l app=sleep -n insidemesh -o jsonpath={.items..metadata.name}) -c sleep -n insidemesh -- curl http://productpage.default:9080 -s -o /dev/null -w "sleep.insidemesh to http://productpage.default:9080: -> HTTP_STATUS: %{http_code}\n"
```

> Note: every workload **with sidecard** can access book info services (HTTP_STATUS = 200)

### Create another namespace, outsidemesh, and deploy sleep **without a sidecar**:

```bash
kubectl create ns outsidemesh
kubectl apply -f samples/sleep/sleep.yaml -n outsidemesh
```

Verify setup by sending an http request (using curl command) from sleep pod (namespace: outsidemesh) to productpage.default:9080:

```bash
kubectl exec $(kubectl get pod -l app=sleep -n outsidemesh -o jsonpath={.items..metadata.name}) -c sleep -n outsidemesh -- curl http://productpage.default:9080 -s -o /dev/null -w "sleep.outsidemesh to http://productpage.default:9080: -> HTTP_STATUS: %{http_code}\n"
```
> Note: every workload **without sidecard** can not access book info services (HTTP_STATUS = 000)
