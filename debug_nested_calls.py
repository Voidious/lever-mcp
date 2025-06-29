#!/usr/bin/env python3
"""Debug nested function calls in expressions."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import evaluate_expression, lists

def debug_nested_calls():
    """Debug nested function calls."""
    
    print("=== Debugging Nested Function Calls ===\n")
    
    # Test simple map
    result1 = lists.fn(items=["alice", "bob"], operation="map", expression="strings.upper_case(item)")
    print(f"Direct lists.fn map: {result1}")
    
    # Test if strings functions are available in expression evaluation
    result2 = evaluate_expression('strings.upper_case("test")', {"item": "alice"})
    print(f"strings.upper_case in evaluate_expression: {result2}")
    
    # Test if item resolution works
    result3 = evaluate_expression('item', {"item": "alice"})
    print(f"item resolution: {result3}")
    
    # Test expression evaluation with item
    result4 = evaluate_expression('strings.upper_case(item)', {"item": "alice"})
    print(f"strings.upper_case(item) with context: {result4}")
    
    # Test what happens inside lists.map
    print("\nTesting what happens inside lists.map...")
    result5 = evaluate_expression('lists.map({"alice", "bob"}, "strings.upper_case(item)")', {})
    print(f"lists.map result: {result5}")

if __name__ == "__main__":
    debug_nested_calls()