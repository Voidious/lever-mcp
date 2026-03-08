#!/usr/bin/env python3
"""
Comprehensive test suite for Lua tool call functionality.
Tests both positional and table-based argument syntax for all MCP tools.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_comprehensive_tests():
    """Run all test classes."""
    from tests.lua.lua_tool_calls.test_collections import (
        TestLuaDictsOperations,
        TestLuaListsOperations,
        TestLuaStringsOperations,
    )
    from tests.lua.lua_tool_calls.test_function_returns_and_edge_cases import (
        TestLuaEdgeCases,
        TestLuaErrorHandling,
        TestLuaFunctionReturns,
    )
    from tests.lua.lua_tool_calls.test_generate_and_any import (
        TestGenerateWrapParameter,
        TestLuaAnyOperations,
        TestLuaGenerateOperations,
    )
    from tests.lua.lua_tool_calls.test_tool_references import (
        TestLuaToolFunctionReferences,
    )
    from tests.lua.lua_tool_calls.test_wrap_parameters import (
        TestPositionalVsTableWrapParameter,
    )
    from tests.lua.lua_tool_calls.test_wrapper_functions import TestLuaWrapperFunctions
    import traceback

    test_classes = [
        TestLuaStringsOperations,
        TestLuaListsOperations,
        TestLuaDictsOperations,
        TestLuaAnyOperations,
        TestLuaGenerateOperations,
        TestLuaFunctionReturns,
        TestLuaEdgeCases,
        TestLuaErrorHandling,
        TestLuaToolFunctionReferences,
        TestLuaWrapperFunctions,
        TestPositionalVsTableWrapParameter,
        TestGenerateWrapParameter,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()

        # Get all test methods
        test_methods = [
            method for method in dir(instance) if method.startswith("test_")
        ]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"❌ {method_name}: {str(e)}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
                traceback.print_exc()

    print(f"\n{'=' * 60}")
    print("COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests / total_tests) * 100:.1f}%")

    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  {class_name}.{method_name}: {error}")
    else:
        print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_comprehensive_tests()
