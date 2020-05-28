from kubernetes import client, config
from kubernetes.stream import stream 
import time
from datetime import timedelta, datetime

config.load_kube_config()
client_apis = client.CoreV1Api()

def test_can_send_request_via_mTLS_with_certificate():
    list_namespaces = ['foo','bar']
    pod_name = "sleep"
    wait_for_all_pods_ready(list_namespaces, pod_name)
    verify_can_send_request_via_mTLS_with_certificate(list_namespaces, pod_name)

def test_cannot_send_request_via_mTLS_with_certificate():
    list_namespaces = ['legacy']
    pod_name = "sleep"
    wait_for_all_pods_ready(list_namespaces, pod_name)
    verify_cannot_send_request_via_mTLS_without_certificate(list_namespaces, pod_name)

def verify_can_send_request_via_mTLS_with_certificate(list_namespaces: list, pod_name: str):
    for src_namespace in list_namespaces:
        pod_list = client_apis.list_namespaced_pod(src_namespace)
        for pod in pod_list.items:
            if pod_name == pod.metadata.labels.get("app",""):
                assert_request(pod, src_namespace, list_namespaces, lambda status_code: status_code == "200")

def verify_cannot_send_request_via_mTLS_without_certificate(list_namespaces: list, pod_name: str):
    for src_namespace in list_namespaces:     
        pod_list = client_apis.list_namespaced_pod(src_namespace)
        for pod in pod_list.items:
            if pod_name == pod.metadata.labels.get("app",""):
                assert_request(pod, src_namespace, ["foo", "bar"], lambda status_code: status_code != "200")

def assert_request(pod, src_namespace, list_namespaces, assert_function):
    for dest_namespace in list_namespaces:
        resp=stream(client_apis.connect_get_namespaced_pod_exec,name=pod.metadata.name,namespace=src_namespace,command=["curl", "--connect-timeout","3" ,"http://httpbin.{0}.global:8000/ip".format(dest_namespace),"-s","-o","/dev/null","-w","%{http_code}\n"],stderr=True,stdout=True,container="sleep")
        print(resp)
        assert_function(str(resp))

def wait_for_all_pods_ready(list_namespaces: list ,pod_name: str):
    for src_namespace in list_namespaces:
        wait_for_pod_ready(src_namespace, pod_name)

def wait_for_pod_ready(namespace: str = "default", pod_name: str = ""):
    pod_list = client_apis.list_namespaced_pod(namespace)
    if len(pod_list.items) == 0:
        print("Namespace {0} does not exist!".format(namespace))
        return 
    ready_status = "Running"
    current_status = "Pending"
    pod_ready = current_status == ready_status
    start_time = datetime.now()
    total_waiting_time = (datetime.now() - start_time).total_seconds()
    while not pod_ready and total_waiting_time < 30.0 :
        for pod in pod_list.items:
            if pod_name == pod.metadata.labels.get("app",""):
                current_status = pod.status.phase
                print("Pod status: {0}..........!".format(pod.status.phase))
        pod_list = client_apis.list_namespaced_pod(namespace)
        pod_ready = current_status == ready_status
        total_waiting_time = (datetime.now() - start_time).total_seconds()
        time.sleep(1)
