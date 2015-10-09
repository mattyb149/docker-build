{%- if broken|length > 0 %}
Newly Broken Tests:
=================
{%- endif %}
{% for classname, errors in broken.iteritems() if 'suiteErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Suite Errors:
-----------------
  {%- endif -%}
  {%- for suiteError in errors['suiteErrors'] %}
{{ classname }}: {{ suiteError.type }}
```
{{ suiteError.message }}
```
  {%- endfor -%}
{%- endfor -%}
{% for classname, errors in broken.iteritems() if 'caseErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Case Errors:
-----------------
  {% endif %}
  {%- for name, error in errors['caseErrors'].iteritems() -%}
{{ classname }}.{{ name }}: {{ error.type }}
```
{{ error.message }}
```
  {%- endfor -%}
{%- endfor -%}

{%- if fixed|length > 0 %}
Newly Fixed Tests:
=================
{%- endif %}
{% for classname, errors in fixed.iteritems() if 'suiteErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Suite Errors:
-----------------
  {%- endif -%}
  {%- for suiteError in errors['suiteErrors'] %}
{{ classname }}: {{ suiteError.type }}
```
{{ suiteError.message }}
```
  {%- endfor -%}
{%- endfor -%}
{% for classname, errors in fixed.iteritems() if 'caseErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Case Errors:
-----------------
  {% endif %}
  {%- for name, error in errors['caseErrors'].iteritems() -%}
{{ classname }}.{{ name }}: {{ error.type }}
```
{{ error.message }}
```
  {%- endfor -%}
{%- endfor -%}

{%- if stillBroken|length > 0 %}
Still Broken Tests:
===================
{%- endif %}
{% for classname, errors in stillBroken.iteritems() if 'suiteErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Suite Errors:
-----------------
  {%- endif -%}
  {%- for suiteError in errors['suiteErrors'] %}
{{ classname }}: {{ suiteError['after'].type }}
```
{{ suiteError['after'].message }}
```
  {%- endfor -%}
{%- endfor -%}
{% for classname, errors in stillBroken.iteritems() if 'caseErrors' in errors -%}
  {%- if loop.index == 1 -%}
Test Case Errors:
-----------------
  {% endif %}
  {%- for name, error in errors['caseErrors'].iteritems() -%}
{{ classname }}.{{ name }}: {{ error['after'].type }}
```
{{ error['after'].message }}
```
  {%- endfor -%}
{%- endfor -%}

