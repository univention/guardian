package univention.base

import future.keywords.if

test_get_permissions_happy_case if {
	inp = {
		"actor": {
			"id": "actor_id_1",
			"roles": {"ucsschool:users:teacher"},
		},
		"targets": [{
			"old": {"id": "target_id_1"},
			"new": {"id": "target_id_1"},
		}],
		"namespaces": {"ucsschool": {"users", "groups"}},
		"contexts": {},
		"extra_args": {},
	}
	result = get_permissions with input as inp
	print("TEST_DEBUG -- result: ", result)
	result == {{
		"target_id": "target_id_1",
		"permissions": {
			{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"},
			{"appName": "ucsschool", "namespace": "users", "permission": "read_last_name"},
			{"appName": "ucsschool", "namespace": "users", "permission": "write_password"},
			{"appName": "ucsschool", "namespace": "users", "permission": "export"},
		},
	}}
}

test_get_permissions_empty_input if {
	inp = {}
	result = get_permissions with input as inp
	print("TEST_DEBUG -- result: ", result)
	result == set()
}
