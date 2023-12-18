package univention.target_field_equals_actor_field_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

target_field_equals_actor_field_parametrize := [
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
			"actor": {"id": "foo", "roles": [], "attributes": {"email2": "foo"}},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo", "roles": [], "attributes": {"email": "foo"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"target_field": "email", "actor_field": "email2"},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo", "roles": [], "attributes": {"email2": "foo"}},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo", "roles": [], "attributes": {"email": "bar"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"target_field": "email", "actor_field": "email2"},
		"result": false,
	},
]

test_target_field_equals_actor_field if {
	every case in target_field_equals_actor_field_parametrize {
		result := condition("guardian:builtin:target_field_equals_actor_field", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
