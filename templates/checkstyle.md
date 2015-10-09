Changed files:
==============
{%- for file in fileList %}
  {{file}}
{%- endfor %}

Checkstyle violations:
----------------------
{% for violation in violations -%}
  {%- if loop.index == 0 -%}
    Errors:
    File {{ violation.filename }}
    {%- for error in violation.errors -%}
      {{ loop.index }}. Message: {{error.message}} at Line: {{ error.line }} Column: {{ error.column }}
    {%- endfor -%}
  {%- endif -%}
{%- else -%}
  No errors found
{%- endfor %}
