# Prototype — Testing Strict handling of missing template variables

Note: This is an experimental prototype made for understanding the problem space better and to get early feedback from maintainers.  
This is **not** a final design or production implementation.

## Goal

I made small localized changes in my Django fork to understand how missing template variables are currently handled internally and to check if strict behaviour can be introduced with minimal changes.

This small prototype/code-implementation is meant to showcase my thought-process alignment with the GSOC-2026 "Template ergonomics and missing variables" project and mentors.

---

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

### 2. Resolving Variables:

Currently the missing variables are converted to empty output, but when `strict_variables=True` missing variable exceptions are re-raised instead of ignored. this happens during variable lookup and filter resolution.

### 3. {% if %} conditions:

Currently the missing variables inside the `{% if %}` become false and rendering continues.

But in the strict mode, missing varibales raise `VariableDoesNotExist`

### 4. {% for %} Loops:

Currently missing loop variables resolve to `None` after failure is silently handeled so the loop renders as empty.

But in strict mode missing variables raises error, if variable is missing insted of silenty failing.

### Summary of Strict mode:

Having a toggle flag `strict_variables` gives developers option to evaluate missing variable errors.

The goal here is early experimentation and validation from mentors, not final API design.

## Next Steps

Need to discuss API design properly to decide where strict mode should live (template level, engine level, settings, etc.) while keeping current behaviour safe.

Behaviour rules should be clearly defined across rendering, if conditions, for loops, filters, and nested lookups so things stay consistent and predictable.

Need to check compatibility carefully, especially with Django admin and reusable templates where missing variables might be used intentionally.

Validation should be done with real templates to see where strict mode actually helps and where it creates problems.

Further improvements will depend on maintainer feedback and discussion before moving toward a final implementation direction.




---
