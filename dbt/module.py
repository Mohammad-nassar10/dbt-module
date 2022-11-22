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
    # transformation_cols = conf['transformation_cols']
    asset_creds = conf['asset_creds']
    # dremio_creds = conf['dremio_creds']
    # username = dremio_creds[0]
    # password = dremio_creds[1]
    
    # create dbt profile and dbt project

    # get the name of the columns need to be removed
    transformation_cols = conf['transformation_cols']
    # the rest of the columns
    cols = "name, phone"

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
    
    # # add the schema for the dbt model
    # model_schema = {"version": 2, "models": [{"name": "custview", "description": "View of customers without the id field"}]}
    # with open("models/schema1.yml", "w+") as model_schema:
    #     data = yaml.dump(model_schema, model_schema, sort_keys=False, default_flow_style=False)

    with open("models/schema.yml", "w+") as model_schema:
        l1 = "version: 2"
        l2 = "models:"
        l3 = "  - name: view"
        l4 = '    description: "View of customers without the id field"'
        lines = [l1, l2, l3, l4]
        model_schema.writelines('\n'.join(lines) + '\n')

    os.system("python3.8 dbt-rpc/dbt_rpc/__main__.py serve")
