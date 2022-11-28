[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Dbt Module

This module configures and runs a [dbt-rpc](https://docs.getdbt.com/reference/commands/rpc) server that can work with trino or dremio and can be extended to other [adapters](https://docs.getdbt.com/docs/supported-data-platforms) that [dbt](https://github.com/dbt-labs/dbt-core) supports


### Before you begin
Ensure that you have the following:

- Helm 3.3 or greater must be installed and configured on your machine.
- Kubectl 1.18 or newer must be installed on your machine.
- Access to a Kubernetes cluster such as Kind as a cluster administrator.
- Running Trino or Dremio server.

### Install fybrik
Install Fybrik v1.1 using the [Quick Start](https://fybrik.io/v1.1/get-started/quickstart/), without the section of `Install modules`.


### Register the Fybrik module:
Apply the fybrik module using the following command:
```bash
kubectl apply -f module.yaml -n fybrik-system
```


### Create namespace
```bash
kubectl create namespace fybrik-sample
kubectl config set-context --current --namespace=fybrik-sample
```

### Create an asset
Create a table in your running Trino or Dremio table. For example, in Trino, create a table `customers` with the columns `[custkey, name, phone]` in `iceberg` catalog and `icebergtrino` schema.

### Register the asset
Replace the values of `host` and `port` in `sample/asset1.yaml` file according to your running Trino/Dremio server. Then, add the asset to the internal catalog using the following command:

```bash
kubectl apply -f sample/asset1.yaml
```
The asset has been marked as a `finance` data and the column `custkey` has been marked with `PII` tag.

### Register the access secret
Replace the values for `access_key` and `secret_key` in `sample/secret1.yaml` file with the `user` and `password` of the running Trino/Dremio and run the following command:
```bash
kubectl apply -f sample/secret1.yaml
```

### Define data access policy
Register a policy. The example policy removes columns tagged as `PII` from datasets marked as `finance`.
```bash
kubectl -n fybrik-system create configmap sample-policy --from-file=sample/sample-policy.rego
kubectl -n fybrik-system label configmap sample-policy openpolicyagent.org/policy=rego
while [[ $(kubectl get cm sample-policy -n fybrik-system -o 'jsonpath={.metadata.annotations.openpolicyagent\.org/policy-status}') != '{"status":"ok"}' ]]; do echo "waiting for policy to be applied" && sleep 5; done
```

### Deploy Fybrik application
Run the following command to apply the `fybrikapplication` that triggers the dbt-module:

```bash
kubectl apply -f sample/fybrikapplication.yaml
```

Wait for the `fybrikapplication` to be ready (could take a few minutes):
```bash
while [[ ($(kubectl get fybrikapplication dbt-sample-app -o 'jsonpath={.status.ready}') != "true") || ($(kubectl get fybrikapplication dbt-sample-app -o 'jsonpath={.status.assetStates.fybrik-sample/dataset1.conditions[?(@.type == "Ready")].status}') != "True") ]]; do echo "waiting for FybrikApplication" && sleep 5; done
```

Use port-forward to connect to `dbt-rpc` server on `http://localhost:9047/`:
```bash
kubectl port-forward svc/dbt-sample-app-fybrik-sample-read -n fybrik-blueprints 8580:80 &
```

You can run different [dbt-rpc commands](https://docs.getdbt.com/reference/commands/rpc) against the running `dbt-rpc` server. For example, you can run the following command to run the `dbt` model that creates a governed view:
```bash
curl -d "{\"jsonrpc\": \"2.0\", \"id\": 2, \"method\": \"run\", \"params\": {\"threads\": 1}}" --header "Content-Type: application/json" http://localhost:8580/jsonrpc
``` 
Now, you can see in the running Trino/Dremio that a new view was created with the name `view`.

In function `_get_exec_node` in `dbt/dbt-rpc/dbt_rpc/task/sql_commands.py` file we added an example code for modifying the `sql` queries that select from the `customers` table to select from the new `view` table. Thus, if you try to run the query `select * from "iceberg"."icebergtrino".customers` you will get the result without the `custkey` column which is `PII` data. Use the following command to run the sql query (change the field `sql` to the base64-encoded sql query):

```bash
curl -d "{\"jsonrpc\": \"2.0\", \"id\": 2, \"method\": \"run_sql\", \"params\": {\"sql\": \"<sql query base64-encoded>\", \"timeout\": 600, \"name\": \"test_query\"}}" --header "Content-Type: application/json" http://localhost:8580/jsonrpc
```
This command will return, as part of the result, a `request_token` field. Use the `request_token` with a `poll` request to get the data according to the followng command:

```bash
curl -d "{\"jsonrpc\": \"2.0\", \"id\": \"a\", \"method\": \"poll\", \"params\": {\"request_token\": \"<request_token>\", \"logs\": true, \"logs_start\": 0}}" --header "Content-Type: application/json" http://localhost:8580/jsonrpc
```
In the resulting response the columns names and values will appear in the `"table"` key. You can see that the result includes only columns `[name, phone]` without the column `custkey`.


### Cleanup
1. Stop kubectl port-forward processes (e.g., using `pkill kubectl`)
1. Delete the `fybrikapplication`:
    ```bash
    kubectl delete -f sample_assets/fybrikapplication.yaml
    ```
1. Delete the `fybrik-sample` namespace:
    ```bash
    kubectl delete namespace fybrik-sample
    ```
1. Delete the policy created in the `fybrik-system` namespace:
    ```bash
    NS="fybrik-system"; kubectl -n $NS get configmap | awk '/sample/{print $1}' | xargs  kubectl delete -n $NS configmap
    ```
