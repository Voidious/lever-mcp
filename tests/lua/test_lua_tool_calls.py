#!/usr/bin/env python3


def run_comprehensive_tests():
    """Run all test classes."""
    from tests.lua.lua_tool_calls.test_dicts_any import (
        TestLuaAnyOperations,
        TestLuaDictsOperations,
    )
    from tests.lua.lua_tool_calls.test_function_references import (
        TestLuaToolFunctionReferences,
        TestLuaWrapperFunctions,
    )
    from tests.lua.lua_tool_calls.test_generate_edge_cases import (
        TestLuaEdgeCases,
        TestLuaErrorHandling,
        TestLuaFunctionReturns,
        TestLuaGenerateOperations,
    )
    from tests.lua.lua_tool_calls.test_strings_lists import (
        TestLuaListsOperations,
        TestLuaStringsOperations,
    )
    from tests.lua.lua_tool_calls.test_wrap_parameters import (
        TestGenerateWrapParameter,
        TestPositionalVsTableWrapParameter,
    )
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
