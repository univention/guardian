package univention.target_field_not_equals_value_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

target_field_not_equals_value_parametrize := [
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
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo", "roles": [], "attributes": {"email": "foo"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "email", "value": "bar"},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo"},
			"actor_role": {},
			"target": {
				"old": {"id": "notfoo", "roles": [], "attributes": {"email": "foo"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "email", "value": "foo"},
		"result": false,
	},
]

test_target_field_not_equals_value if {
	every case in target_field_not_equals_value_parametrize {
		result := condition("guardian:builtin:target_field_not_equals_value", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
