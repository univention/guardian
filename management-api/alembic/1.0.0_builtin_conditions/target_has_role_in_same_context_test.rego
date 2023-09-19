package univention.target_has_role_in_same_context_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

target_has_role_in_same_context_parametrize := [
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
		"result": false,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {
				"role": "guardian:role:role2",
				"context": "a1:n1:c1",
			},
			"target": {
				"old": {
					"id": "notfoo",
					"roles": ["guardian:role:role1&a1:n1:c1"],
				},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"role": "guardian:role:role1"},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {
				"role": "guardian:role:role1",
				"context": "a1:n1:c3",
			},
			"target": {
				"old": {
					"id": "notfoo",
					"roles": [
						"guardian:role:role1&a1:n1:c1",
						"guardian:role:role1&a1:n1:c2",
					],
				},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"role": "guardian:role:role1"},
		"result": false,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {
				"role": "guardian:role:role2",
				"context": "a1:n1:c1",
			},
			"target": {
				"old": {
					"id": "notfoo",
					"roles": [
						"guardian:role:role1&a1:n1:c1",
						"guardian:role:role1&a1:n1:c2",
					],
				},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"role": "guardian:role:role1"},
		"result": true,
	},
]

test_target_has_role_in_same_context if {
	every case in target_has_role_in_same_context_parametrize {
		result := condition("guardian:builtin:target_has_role_in_same_context", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
