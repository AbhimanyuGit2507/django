# Prototype: Strict Handling of Missing Template Variables

> Note: This is an experimental prototype to validate strict handling of missing variables in Django templates. It is not a final API design.

## Goal

Validate whether missing template variables can be surfaced as exceptions (instead of silent fallbacks) with minimal, centralized changes to Django's template resolution pipeline, while preserving default behavior.

## Core Idea

Move missing-variable handling from silent fallback to controlled exception propagation, enforced at the resolution layer rather than in individual template nodes.

## Current Django Flow

1. Variable.resolve()
2. Variable._resolve_lookup()
   - Raises VariableDoesNotExist on lookup failure.
3. FilterExpression.resolve()
   - Catches VariableDoesNotExist.
   - Returns fallback values:
     - empty string
     - string_if_invalid
     - None (for paths using ignore_failures=True, such as loop sequence resolution)

Resulting default behavior:
- {{ missing }} -> empty string
- {% if missing %} -> false branch
- {% for x in missing %} -> empty iteration

## Files Changed

- [django/django/template/context.py](https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/context.py)  
  Added strict_variables support in Context and ensured it propagates correctly.

- [django/django/template/base.py](https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/base.py)  
  Centralized strict missing-variable behavior in variable/filter resolution and added missing-variable hook handling.

- [django/django/template/defaulttags.py](https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/defaulttags.py)  
  Updated control-flow behavior (especially loop resolution) to avoid silent missing-variable handling in strict mode.

- [django/django/template/defaultfilters.py](https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/django/template/defaultfilters.py)  
  Added exists filter implementation using missing-variable resolution hook behavior.

- [django/tests/template_tests/test_strict_mode.py](https://github.com/AbhimanyuGit2507/django/blob/strict-template-prototype/tests/template_tests/test_strict_mode.py)  
  Added and expanded high-value strict-mode and exists-filter test coverage (edge cases, chaining, nested lookups, strict/non-strict matrix).

## Changes Introduced

### 1) Strict Mode Flag

    Context(..., strict_variables=True)
    Template(..., strict_variables=True)

- Default mode: unchanged Django behavior.
- Strict mode: propagate VariableDoesNotExist instead of swallowing it.
- Flag is carried through context lifecycle and rendering paths.

### 2) Resolution-Layer Enforcement

Modified points:
- Variable._resolve_lookup
- FilterExpression.resolve

Behavior:

    try:
        value = self._resolve_lookup(context)
    except VariableDoesNotExist:
        if context.strict_variables:
            raise
        return fallback

In strict mode:
- Missing variable exceptions are not swallowed.
- No fallback to empty string or None for missing resolution.

### 3) Loop Behavior in Strict Mode

Default behavior allows missing loop sources to become empty iterations through ignore_failures=True.

Prototype behavior:
- In strict mode, missing loop sequence resolution is not silently ignored.
- {% for x in missing %} raises VariableDoesNotExist.

### 4) Uniform Semantics Across Template Constructs

Because enforcement is centralized in resolution, behavior is consistent:

| Construct | Strict mode behavior |
|---|---|
| {{ var }} | raises |
| {% if var %} | raises |
| {% for x in var %} | raises |
| {{ obj.attr }} | raises |

No node-specific strict logic is required.

### 5) Filter-Level Missing-Variable Hook

Added optional hook:

    filter._resolve_missing_variable(context, variable)

Hook semantics:
- Triggered only when variable resolution fails.
- Applied only to the first filter in the chain.
- If hook handles the miss, its return value continues through remaining filters.
- Otherwise fallback or raise behavior proceeds as normal.

### 6) exists Filter

Implemented via missing-variable hook.

Usage:
- {% if variable|exists %}

Behavior:
- Returns False if resolution fails.
- Returns True if variable exists, even when value is falsy (None, False, 0, empty string).

This distinguishes:
- variable is missing
- variable exists but is falsy

## Edge Cases Considered

- Nested lookups (a.b.c) fail at first missing segment.
- Callable resolution behavior remains intact.
- SimpleLazyObject resolution remains compatible.
- Filter chaining behavior is deterministic.
- string_if_invalid paths are bypassed in strict missing-variable failure cases.
- default filter does not rescue missing variables in strict mode when resolution fails first.
- Post-exists chaining behaves consistently:
  - {{ missing|exists|upper }} -> FALSE
  - {{ missing|exists|exists }} -> True
- Ordering remains explicit:
  - {{ missing|upper|exists }} raises in strict mode.

## What Was Verified

- Strict mode behavior across:
  - rendering
  - conditionals
  - loops
  - filters
- Default (non-strict) behavior remains unchanged.
- Dedicated strict-mode template tests pass.
- Real-world template exercise performed with Django-Oscar.
- No structural rewrite of template node classes required.

## Non-Goals (Prototype Scope)

- Final public API naming and shape.
- Backward-compatibility policy decisions.
- Full framework-wide rollout strategy.

## How to Try This Locally

### 1) Clone the Fork

    git clone https://github.com/AbhimanyuGit2507/django.git
    cd django
    git checkout strict-template-prototype

### 2) Set Up Environment

    python -m venv venv
    source venv/bin/activate
    pip install -e .

### 3) Run Prototype Tests

    python tests/runtests.py template_tests.test_strict_mode -v 2

### 4) Minimal Example

    from django.template import Context, Template

    # Default behavior
    t = Template("Hello {{ missing }}")
    print(t.render(Context({})))
    # "Hello "

    # Strict mode
    t = Template("Hello {{ missing }}")
    ctx = Context({}, strict_variables=True)
    t.render(ctx)
    # raises VariableDoesNotExist

### 5) exists Filter Example

    {% if missing|exists %}
        Exists
    {% else %}
        Missing
    {% endif %}

Output:

    Missing

### 6) Real Project Testing (Optional)

- Point a Django project to this fork.
- Enable strict mode in the template context path.
- Observe missing-variable failures during rendering.

## Key Takeaways

- Missing-variable behavior can be controlled centrally.
- Strict handling does not require template syntax changes.
- Resolution-layer enforcement is sufficient for broad consistency.
- Filter hook enables safe extensibility with low complexity.
- The prototype integrates cleanly with current Django template internals.
