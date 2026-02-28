# Prototype for Pre-Proposal: Testing Strict handling of missing template variables (Abhimanyu Negi)

Note: This is an experimental prototype made for understanding the problem space better and to **get feedback from maintainers**.  
This is **not** a final design or production implementation.

## Goal

I made small localized changes in my Django fork to understand how missing template variables are currently handled internally and to check if strict behaviour can be introduced with minimal changes.

This small prototype/code-implementation is meant to showcase my thought-process alignment with the GSOC-2026 "Template ergonomics and missing variables" project and mentors.

---

### Files changed:

- Context flag (strict_variables)
https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/context.py

- Variable resolution handling
https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/base.py

- If / for tag behaviour
https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/defaulttags.py

- Prototype tests
https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/tests/template_tests/test_strict_mode.py

### Test Results:

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/e26d074b-6383-4c18-82e4-67f21b8b385b" />



## Strict mode behaviour:

When `strict_variables=True` in Context:

- missing variables raise `VariableDoesNotExist`
- this applies to rendering, if conditions, for loops, and nested access
- existing variables behave normally

## Explaination of Concept:

### 1. Context Flag:

Added an internal context flag for strict variable handling 

`strict_variables=False | strict_variables=True`

the flag also gets copied when context is copied, this makes the behaviour consistent.

example:

`context = Context({"existing": "world"}, strict_variables=True)`

### 2. Resolving Variables:

Currently the missing variables are converted to empty output, but when `strict_variables=True` missing variable exceptions are re-raised instead of ignored. this happens during variable lookup and filter resolution.

example:

```
template = Template("Hello {{ missing_var }}!", engine=self.engine)
context = Context({}, strict_variables=True)

with self.assertRaises(VariableDoesNotExist):
    template.render(context)
```

### 3. {% if %} conditions:

Currently the missing variables inside the `{% if %}` become false and rendering continues.

But in the strict mode, missing varibales raise `VariableDoesNotExist`

example:

```
template = Template(
    "{% if missing_var %}yes{% else %}no{% endif %}",
    engine=self.engine,
)
context = Context({}, strict_variables=True)

with self.assertRaises(VariableDoesNotExist):
    template.render(context)
```

### 4. {% for %} Loops:

Currently missing loop variables resolve to `None` after failure is silently handeled so the loop renders as empty.

But in strict mode missing variables raises error, if variable is missing insted of silenty failing.

example:
```
template = Template(
    "{% for item in missing_list %}{{ item }}{% empty %}empty{% endfor %}",
    engine=self.engine,
)
context = Context({}, strict_variables=True)

with self.assertRaises(VariableDoesNotExist):
    template.render(context)
```

### Summary of Strict mode:

Having a toggle flag `strict_variables` gives developers option to evaluate missing variable errors.

The goal here is early experimentation and validation from mentors, not final API design.

## Next Steps

This prototype only checks feasibility.  
Next steps are deciding API design, defining consistent behavior across template constructs, and validating compatibility with admin and reusable templates based on maintainer feedback.

### Authored by: [Abhimanyu Negi](https://github.com/AbhimanyuGit2507/)




---
