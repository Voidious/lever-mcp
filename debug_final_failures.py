#!/usr/bin/env python3
"""Debug the final 4 failing tests."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import evaluate_expression

def debug_final_failures():
    """Debug the last 4 failing tests."""
    
    print("=== Debugging Final 4 Failing Tests ===\n")
    
    # 1. test_any_contains
    print("1. Testing any.contains:")
    result1 = evaluate_expression('any.contains("hello world", "world")', {})
    print(f"any.contains('hello world', 'world'): {result1}")
    
    result2 = evaluate_expression('any.contains({1, 2, 3}, 2)', {})
    print(f"any.contains({{1, 2, 3}}, 2): {result2}")
    
    # 2. test_any_is_equal  
    print("\n2. Testing any.is_equal:")
    result3 = evaluate_expression('any.is_equal("hello", "hello")', {})
    print(f"any.is_equal('hello', 'hello'): {result3}")
    
    result4 = evaluate_expression('any.is_equal({value={a=1}, param={a=1}})', {})
    print(f"any.is_equal table syntax: {result4}")
    
    # 3. test_mixed_syntax_in_expression
    print("\n3. Testing mixed syntax:")
    result5 = evaluate_expression('lists.map({items={"a", "b"}}, "strings.upper_case(item)")', {})
    print(f"Mixed syntax result: {result5}")
    
    # Let's test the components separately
    result6 = evaluate_expression('strings.upper_case("a")', {})
    print(f"strings.upper_case('a'): {result6}")
    
    # 4. test_nested_function_calls
    print("\n4. Testing nested function calls:")
    result7 = evaluate_expression('''
        lists.filter_by(
            {items={{name="Alice", age=25}, {name="Bob", age=17}}}, 
            expression="age >= 18"
        )
    ''', {})
    print(f"Nested function calls result: {result7}")
    
    # Test simpler filter_by
    result8 = evaluate_expression('lists.filter_by({{age=25}}, "age >= 18")', {})
    print(f"Simple filter_by: {result8}")

if __name__ == "__main__":
    debug_final_failures()