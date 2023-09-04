package univention.base

import future.keywords.if

test_get_permissions if {
	inp = {
		"actor": {},
		"targets": [{
			"old": {"id": "target_id_1"},
			"new": {"id": "target_id_1"},
		}],
		"namespaces": set(),
		"contexts": set(),
		"extra_args": {},
	}
	result = get_permissions with input as inp
	print("TEST_DEBUG -- result: ", result)
	result == {{
		"target_id": "target_id_1",
		"permissions": set(),
	}}
}
