{% if target.name == "trino" %}
  {{ config(catalog="iceberg",schema="icebergtrino")}}
{% endif %}
select name, phone
{% if target.name == "trino" %}
  from "{{ var("trino_catalog") }}"."{{ var("trino_schema") }}".customers
{% endif %}
{% if target.name == "dremio" %}
  from "{{ var("dremio_catalog") }}"."{{ var("dremio_schema") }}".customers
{% endif %}
