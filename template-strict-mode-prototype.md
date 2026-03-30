# Prototype — Strict Handling of Missing Template Variables

> Experimental prototype. Not final API.

---

## Core Idea

Control missing-variable behavior at the **resolution layer** instead of template nodes.

Switch:
- silent fallback → exception propagation (opt-in)

---

## Strict Mode

```python
Context(..., strict_variables=True)
Template(..., strict_variables=True)
```

default → unchanged Django behavior
strict → raise VariableDoesNotExist
Resolution Flow Change

Modified:

```
Variable._resolve_lookup
FilterExpression.resolve
try:
    value = self._resolve_lookup(context)
except VariableDoesNotExist:
    if context.strict_variables:
        raise
    return fallback
```

## Loop Behavior

**Current:**
`sequence.resolve(context, ignore_failures=True)`

**Strict mode:**
- disable `ignore_failures`
- `{% for x in missing %}` → raises `VariableDoesNotExist`

---

## Filter Hook

`filter._resolve_missing_variable(context, variable)`

**Flow:**
```
resolve fail
  → check first filter
    → hook → handle
    → else → raise / fallback
```

---

## exists Filter

```django
{% if variable|exists %}
```

- missing → `False`  
- exists (even falsy) → `True`  

---

## Key Edge Cases

- `a.b.c` → fail at first missing  
- filter chain → hook applied once  
- `|default` not executed in strict  
- `string_if_invalid` bypassed  

**ordering matters:**
- `missing|exists|upper` → OK  
- `missing|upper|exists` → raises  

---

## Django-Oscar Testing

### Setup
- Django-Oscar configured with this fork  
- strict mode enabled globally  
- tested:
  - admin  
  - basket  
  - dashboard routes  

### Injected Failures

```django
{{ gsoc_missing_base }}
{{ basket.fake_attribute.name }}
{{ admin_missing_test }}
```

### Output (Actual Errors)

```
/admin/login/ → VariableDoesNotExist: Failed lookup for key [admin_missing_test]
/en-gb/basket/ → VariableDoesNotExist: Failed lookup for key [fake_attribute]
/en-gb/dashboard/login/ → VariableDoesNotExist: Failed lookup for key [gsoc_missing_base]
```

### Observations
- failures occur at exact lookup point  
- nested lookup stops at first missing  
- no silent propagation  
- templates without missing variables render normally  

---

## Test Execution

```bash
python tests/runtests.py template_tests.test_strict_mode -v 2
```

- strict-mode tests pass  
- existing Django tests unaffected  

---

## Minimal Example

```python
from django.template import Template, Context

Template("{{ missing }}").render(Context({}))
# → ""

Template("{{ missing }}").render(
    Context({}, strict_variables=True)
)
# → VariableDoesNotExist
```
