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
        clusterName: DemoDriveCluster
      controlPlaneSecurityEnabled: true
      caProvider: "KeyfactorCA"
      caAddress: "https://<REPLACE_ME>.thedemodrive.com"
      # Configure the external CA Provider by Keyfactor.
      keyfactor: 
        # Name of certificate authorization
        ca: "<REPLACE_ME>"
        # Using for authentication header
        authToken: ""
        # API path for enroll new certificate from Keyfactor
        enrollPath: "/KeyfactorAPI/Enrollment/CSR"
        # Certificate Template for enroll the new one: Default is Istio
        caTemplate: "Istio"
        # ApiKey from Api Setting
        appKey: "<APPKEY_REPLACE_HERE>"

```
 
3. Customizable Install with **Istioctl**

    ```bash
    istioctl manifest --set installPackagePath=charts apply -f ./demo-configuration.yaml
    ```

4. Deploy Book-Info microservice example of Istio

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
