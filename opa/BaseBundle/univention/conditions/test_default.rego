package univention.conditions

import future.keywords.every
import future.keywords.if

condition_only_if_param_result_true_parametrize := [
	{
		"condition_data": {
			"actor": {},
			"target": {
				"old": {},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
			"parameters": {"result": true},
		},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {},
			"target": {
				"old": {},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
			"parameters": {"result": "hello"},
		},
		"result": false,
	},
	{
		"condition_data": {},
		"result": false,
	},
]

test_condition_only_if_param_result_true if {
	every case in condition_only_if_param_result_true_parametrize {
		result := condition("only_if_param_result_true", case.condition_data)
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
