package univention.actor_field_equals_value_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

actor_field_equals_value_parametrize := [
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
			"actor": {"id": "foo", "roles": [], "attributes": {"email": "foo"}},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo"},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "email", "value": "bar"},
		"result": false,
	},
	{
		"condition_data": {
			"actor": {"id": "foo", "roles": [], "attributes": {"email": "foo"}},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo"},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "email", "value": "foo"},
		"result": true,
	},
]

test_actor_field_equals_value if {
	every case in actor_field_equals_value_parametrize {
		result := condition("guardian:builtin:actor_field_equals_value", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
