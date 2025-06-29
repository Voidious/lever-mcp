#!/usr/bin/env python3
import re

# Read the test file
with open('tests/test_lua_tool_calls.py', 'r') as f:
    content = f.read()

# Extract operation names from test methods
test_methods = re.findall(r'def test_(\w+)', content)

# Categorize by tool
strings_tested = set()
lists_tested = set()
dicts_tested = set()
any_tested = set()
generate_tested = set()
edge_cases = set()

for method in test_methods:
    if method.startswith('string_'):
        op = method.replace('string_', '')
        if op not in ['function_return', 'is_alpha_positional', 'is_alpha_table']:
            strings_tested.add(op)
    elif method.startswith('lists_'):
        op = method.replace('lists_', '')
        if op not in ['function_return', 'every_alias', 'some_alias']:
            lists_tested.add(op)
    elif method.startswith('dicts_'):
        op = method.replace('dicts_', '')
        dicts_tested.add(op)
    elif method.startswith('any_'):
        op = method.replace('any_', '')
        if op != 'function_return':
            any_tested.add(op)
    elif method.startswith('generate_'):
        op = method.replace('generate_', '')
        generate_tested.add(op)
    else:
        edge_cases.add(method)

print('=== STRINGS OPERATIONS TESTED ===')
for op in sorted(strings_tested):
    print('  ' + op)

print('\n=== LISTS OPERATIONS TESTED ===')
for op in sorted(lists_tested):
    print('  ' + op)
    
print('\n=== DICTS OPERATIONS TESTED ===')
for op in sorted(dicts_tested):
    print('  ' + op)
    
print('\n=== ANY OPERATIONS TESTED ===')
for op in sorted(any_tested):
    print('  ' + op)
    
print('\n=== GENERATE OPERATIONS TESTED ===')
for op in sorted(generate_tested):
    print('  ' + op)
    
print('\n=== EDGE CASES/OTHER TESTS ===')
for test in sorted(edge_cases):
    print('  ' + test)

# Now let's check which operations are defined but not tested
print('\n' + '='*60)
print('OPERATIONS DEFINED BUT NOT TESTED')
print('='*60)

# From main.py analysis - operations available in each tool
strings_available = {
    'camel_case', 'capitalize', 'contains', 'deburr', 'ends_with', 'is_alpha',
    'is_digit', 'is_empty', 'is_equal', 'is_lower', 'is_upper', 'kebab_case',
    'lower_case', 'replace', 'reverse', 'sample_size', 'shuffle', 'snake_case',
    'starts_with', 'template', 'trim', 'upper_case', 'xor'
}

lists_available = {
    'all_by', 'every', 'any_by', 'some', 'count_by', 'difference_by', 'filter_by',
    'find_by', 'flat_map', 'group_by', 'intersection_by', 'key_by', 'map',
    'max_by', 'min_by', 'partition', 'pluck', 'reduce', 'remove_by', 'sort_by',
    'uniq_by', 'zip_with', 'chunk', 'compact', 'contains', 'drop', 'drop_right',
    'flatten', 'flatten_deep', 'head', 'index_of', 'initial', 'is_empty',
    'is_equal', 'last', 'nth', 'random_except', 'sample', 'sample_size',
    'shuffle', 'tail', 'take', 'take_right', 'difference', 'intersection',
    'union', 'xor', 'unzip_list', 'zip_lists'
}

dicts_available = {
    'get_value', 'has_key', 'invert', 'is_empty', 'is_equal', 'merge',
    'omit', 'pick', 'set_value'
}

any_available = {'contains', 'eval', 'is_empty', 'is_equal', 'is_nil'}

generate_available = {
    'accumulate', 'cartesian_product', 'combinations', 'cycle', 'permutations',
    'powerset', 'range', 'repeat', 'unique_pairs', 'windowed', 'zip_with_index'
}

# Find missing tests
strings_missing = strings_available - strings_tested
lists_missing = lists_available - lists_tested
dicts_missing = dicts_available - dicts_tested
any_missing = any_available - any_tested
generate_missing = generate_available - generate_tested

print('\nSTRINGS - Missing tests:')
for op in sorted(strings_missing):
    print('  ' + op)

print('\nLISTS - Missing tests:')
for op in sorted(lists_missing):
    print('  ' + op)

print('\nDICTS - Missing tests:')
for op in sorted(dicts_missing):
    print('  ' + op)

print('\nANY - Missing tests:')
for op in sorted(any_missing):
    print('  ' + op)

print('\nGENERATE - Missing tests:')
for op in sorted(generate_missing):
    print('  ' + op)