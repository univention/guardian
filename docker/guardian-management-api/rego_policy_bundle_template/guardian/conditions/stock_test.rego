package univention.stock_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

condition_only_if_param_result_true_parametrize := [
	{
		"condition_data": {
			"actor": {},
			"actor_role": {},
			"target": {
				"old": {},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"result": true},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {},
			"actor_role": {},
			"target": {
				"old": {},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"result": "hello"},
		"result": false,
	},
	{
		"condition_data": {},
		"parameters": {},
		"result": false,
	},
]

test_condition_only_if_param_result_true if {
	every case in condition_only_if_param_result_true_parametrize {
		result := condition("only_if_param_result_true", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
