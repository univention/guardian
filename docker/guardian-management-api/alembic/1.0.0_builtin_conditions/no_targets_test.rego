package univention.no_targets_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

no_targets_parametrize := [
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
		"parameters": {},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {},
			"target": {
				"old": {"id": ""},
				"new": {"id": ""},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {},
			"target": {
				"old": null,
				"new": null,
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {},
			"target": {
				"old": null,
				"new": {"id": "something"},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {},
		"result": false,
	},
]

test_no_targets if {
	every case in no_targets_parametrize {
		result := condition("guardian:builtin:no_targets", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
