package univention.actor_does_not_have_role_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

actor_does_not_have_role_parametrize := [
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
			"actor": {"id": "foo", "roles": ["guardian:role:role1:role2"]},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo"},
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
			"actor": {"id": "foo", "roles": ["guardian:role:role1", "guardian:role:role2"]},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo"},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"role": "guardian:role:role1"},
		"result": false,
	},
]

test_actor_does_not_have_role if {
	every case in actor_does_not_have_role_parametrize {
		result := condition("guardian:builtin:actor_does_not_have_role", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
