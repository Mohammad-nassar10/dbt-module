import utils
import yaml
import os


if __name__ == "__main__":
    print("dbt module")
    # Get the dataset details from configuration
    # conf, adapter_host, adapter_port = utils.get_details_from_conf("../sample-conf.yaml")
    conf = utils.get_details_from_conf()
    print("conf")
    print(conf)
    transformation = conf['transformation']
    
    # get the name of the columns need to be removed
    transformation_cols = conf['transformation_cols']
    # the rest of the columns
    cols = "name, phone"
    adapter = conf['adapter']


    # create profiles.yml
    if adapter['type'] == 'trino':
        adapter_dict = {'fybrik': {'target': 'trino', 'outputs': {'trino': {'type': 'trino', 'method': 'none', 'user': adapter.get('user', ""), 
                        'password': adapter.get('password', ""), 'catalog': adapter.get('catalog', ""), 'schema': adapter.get('schema', ""), 
                        'host': adapter.get('host', "localhost"), 'port': adapter.get('port', 8080), 'threads': 1}}}}
        with open("profiles.yml", "w") as profiles:
            yaml.dump(adapter_dict, profiles, sort_keys=False, default_flow_style=False)

    if adapter['type'] == 'dremio':
        adapter_dict = {'fybrik': {'target': 'dremio', 'outputs': {'dremio': {'type': 'dremio', 'user': adapter.get('user', ""), 'user_ssl': 'false', 
                        'password': adapter.get('password'), 'software_host': adapter.get('host', "localhost"), 'port': adapter.get('port', 8080), 'threads': 1}}}}
        with open("profiles.yml", "w") as profiles:
            yaml.dump(adapter_dict, profiles, sort_keys=False, default_flow_style=False)


    # create a dbt model for creating the governed view
    with open("models/view.sql", "w+") as model_file:
        l1 = '{% if target.name == "trino" %}'
        l2 = '  {{ config(catalog="iceberg",schema="icebergtrino")}}'
        l3 = '{% endif %}'

        l4 = 'select ' + cols
        l5 = '{% if target.name == "trino" %}'
        l6 = '  from "{{ var("trino_catalog") }}"."{{ var("trino_schema") }}".customers'
        l7 = '{% endif %}'
        l8 = '{% if target.name == "dremio" %}'
        l9 = '  from "{{ var("dremio_catalog") }}"."{{ var("dremio_schema") }}".customers'
        l10 = '{% endif %}'
        lines = [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10]
        model_file.writelines('\n'.join(lines) + '\n')
    
    # add the schema for the dbt model
    model_schema_dict = {'version': 2, 'models': [{'name': 'view', 'description': 'View of customers without the id field'}]}
    with open("models/schema.yml", "w") as model_schema:
        data = yaml.dump(model_schema_dict, model_schema, sort_keys=False, default_flow_style=False)

    dbt_command = "python3.8 dbt-rpc/dbt_rpc/__main__.py serve --target " + adapter['type']
    os.system(dbt_command)
