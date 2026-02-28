"""
Tests for experimental prototype strict mode for missing template variables.
This is NOT final API work — only an experimental implementation for behaviour validation.
"""

from django.template import Context, Engine, Template, VariableDoesNotExist
from django.test import SimpleTestCase


class StrictModePrototypeTests(SimpleTestCase):
    """
    Tests for the experimental strict_variables mode prototype.
    
    When strict_variables=False (default): current behavior is maintained
    When strict_variables=True: missing variables raise VariableDoesNotExist
    """

    def setUp(self):
        self.engine = Engine()

    # =========================================================================
    # Variable Rendering Tests: {{ variable }}
    # =========================================================================
    
    def test_missing_variable_default_behavior(self):
        """Missing variable with strict mode OFF → current behavior (empty string)"""
        template = Template("Hello {{ missing_var }}!", engine=self.engine)
        context = Context({"existing": "world"}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "Hello !")

    def test_missing_variable_strict_mode(self):
        """Missing variable with strict mode ON → exception raised"""
        template = Template("Hello {{ missing_var }}!", engine=self.engine)
        context = Context({"existing": "world"}, strict_variables=True)
        
        with self.assertRaises(VariableDoesNotExist):
            template.render(context)

    def test_existing_variable_default_behavior(self):
        """Existing variable with strict mode OFF → normal rendering"""
        template = Template("Hello {{ name }}!", engine=self.engine)
        context = Context({"name": "world"}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "Hello world!")

    def test_existing_variable_strict_mode(self):
        """Existing variable with strict mode ON → normal rendering"""
        template = Template("Hello {{ name }}!", engine=self.engine)
        context = Context({"name": "world"}, strict_variables=True)
        
        result = template.render(context)
        
        self.assertEqual(result, "Hello world!")

    # =========================================================================
    # If Condition Tests: {% if variable %}
    # =========================================================================
    
    def test_missing_variable_in_if_default_behavior(self):
        """Missing variable in if with strict mode OFF → condition evaluates to None/False"""
        template = Template("{% if missing_var %}yes{% else %}no{% endif %}", engine=self.engine)
        context = Context({"existing": "value"}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "no")

    def test_missing_variable_in_if_strict_mode(self):
        """Missing variable in if with strict mode ON → exception raised"""
        template = Template("{% if missing_var %}yes{% else %}no{% endif %}", engine=self.engine)
        context = Context({"existing": "value"}, strict_variables=True)
        
        with self.assertRaises(VariableDoesNotExist):
            template.render(context)

    def test_existing_variable_in_if_default_behavior(self):
        """Existing variable in if with strict mode OFF → normal evaluation"""
        template = Template("{% if show %}yes{% else %}no{% endif %}", engine=self.engine)
        context = Context({"show": True}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "yes")

    def test_existing_variable_in_if_strict_mode(self):
        """Existing variable in if with strict mode ON → normal evaluation"""
        template = Template("{% if show %}yes{% else %}no{% endif %}", engine=self.engine)
        context = Context({"show": True}, strict_variables=True)
        
        result = template.render(context)
        
        self.assertEqual(result, "yes")

    # =========================================================================
    # For Loop Tests: {% for x in variable %}
    # =========================================================================
    
    def test_missing_variable_in_for_default_behavior(self):
        """Missing variable in for with strict mode OFF → empty iteration"""
        template = Template("{% for item in missing_list %}{{ item }}{% empty %}empty{% endfor %}", engine=self.engine)
        context = Context({"existing": [1, 2, 3]}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "empty")

    def test_missing_variable_in_for_strict_mode(self):
        """Missing variable in for with strict mode ON → exception raised"""
        template = Template("{% for item in missing_list %}{{ item }}{% empty %}empty{% endfor %}", engine=self.engine)
        context = Context({"existing": [1, 2, 3]}, strict_variables=True)
        
        with self.assertRaises(VariableDoesNotExist):
            template.render(context)

    def test_existing_variable_in_for_default_behavior(self):
        """Existing variable in for with strict mode OFF → normal iteration"""
        template = Template("{% for item in items %}{{ item }}{% endfor %}", engine=self.engine)
        context = Context({"items": [1, 2, 3]}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "123")

    def test_existing_variable_in_for_strict_mode(self):
        """Existing variable in for with strict mode ON → normal iteration"""
        template = Template("{% for item in items %}{{ item }}{% endfor %}", engine=self.engine)
        context = Context({"items": [1, 2, 3]}, strict_variables=True)
        
        result = template.render(context)
        
        self.assertEqual(result, "123")

    # =========================================================================
    # Nested Attribute Access Tests: {{ obj.attr }}
    # =========================================================================
    
    def test_missing_nested_attribute_default_behavior(self):
        """Missing nested attribute with strict mode OFF → empty string"""
        template = Template("{{ obj.missing_attr }}", engine=self.engine)
        context = Context({"obj": {"existing_attr": "value"}}, strict_variables=False)
        
        result = template.render(context)
        
        self.assertEqual(result, "")

    def test_missing_nested_attribute_strict_mode(self):
        """Missing nested attribute with strict mode ON → exception raised"""
        template = Template("{{ obj.missing_attr }}", engine=self.engine)
        context = Context({"obj": {"existing_attr": "value"}}, strict_variables=True)
        
        with self.assertRaises(VariableDoesNotExist):
            template.render(context)

    # =========================================================================
    # Context Copy Preservation Tests
    # =========================================================================
    
    def test_strict_mode_preserved_in_context_copy(self):
        """Strict mode flag is preserved when context is copied"""
        context = Context({"value": "test"}, strict_variables=True)
        context_copy = context.__copy__()
        
        self.assertTrue(context_copy.strict_variables)

    def test_non_strict_mode_preserved_in_context_copy(self):
        """Non-strict mode flag is preserved when context is copied"""
        context = Context({"value": "test"}, strict_variables=False)
        context_copy = context.__copy__()
        
        self.assertFalse(context_copy.strict_variables)
