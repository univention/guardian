package univention.target_is_self_test

import data.guardian.conditions.condition
import future.keywords.every
import future.keywords.if

target_is_self_parametrize := [
	{
		"condition_data": {
			"actor": {},
			"actor_role": "",
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
			"actor_role": "",
			"target": {
				"old": {"id": "notfoo"},
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
			"actor_role": "",
			"target": {
				"old": {"id": "foo"},
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
			"actor": {"id": "foo", "attributes": {"uid": "foo"}},
			"actor_role": "",
			"target": {
				"old": {"id": "foo", "attributes": {"uid": "foo"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "uid"},
		"result": true,
	},
	{
		"condition_data": {
			"actor": {"id": "foo", "attributes": {"uid": "foo"}},
			"actor_role": "",
			"target": {
				"old": {"id": "foo", "attributes": {"uid": "notfoo"}},
				"new": {},
			},
			"namespaces": {},
			"contexts": set(),
			"extra_args": {},
		},
		"parameters": {"field": "uid"},
		"result": false,
	},
]

test_target_is_self if {
	every case in target_is_self_parametrize {
		result := condition("guardian:builtin:target_is_self", case.parameters, case.condition_data)

		# regal: ignore:print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
