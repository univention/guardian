package univention.base_test

import data.univention.base.check_permissions
import data.univention.base.get_permissions
import future.keywords.every
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

	# regal ignore: print-or-trace-call
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

test_get_permissions_null_namespaces if {
	inp = {
		"actor": {
			"id": "actor_id_1",
			"roles": {"ucsschool:users:teacher"},
		},
		"targets": [{
			"old": {"id": "target_id_1"},
			"new": {"id": "target_id_1"},
		}],
		"namespaces": null,
		"contexts": null,
		"extra_args": {},
	}
	result = get_permissions with input as inp

	# regal ignore: print-or-trace-call
	print("TEST_DEBUG -- result: ", result)
	result == {{
		"target_id": "target_id_1",
		"permissions": {
			{"appName": "OX", "namespace": "mail", "permission": "edit-spam-filter"},
			{"appName": "OX", "namespace": "mail", "permission": "export"},
			{"appName": "ucsschool", "namespace": "users", "permission": "export"},
			{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"},
			{"appName": "ucsschool", "namespace": "users", "permission": "read_last_name"},
			{"appName": "ucsschool", "namespace": "users", "permission": "write_password"},
		},
	}}
}

test_get_permissions_filtering if {
	role_capability_mapping = {
		"ucsschool:users:teacher": [
			{
				"appName": "ucsschool",
				"conditions": [],
				"namespace": "users",
				"permissions": [
					"read_first_name",
					"read_last_name",
				],
				"relation": "AND",
			},
			{
				"appName": "ucsschool",
				"conditions": [],
				"namespace": "groups",
				"permissions": ["read_display_name"],
				"relation": "AND",
			},
			{
				"appName": "ucsschool",
				"conditions": [],
				"namespace": "exams",
				"permissions": ["collect_exam"],
				"relation": "AND",
			},
			{
				"appName": "ucsschool",
				"conditions": [
					{
						"name": "ucsschool_users_target_has_same_school",
						"parameters": {},
					},
					{
						"name": "target_has_role",
						"parameters": {"role": "ucsschool:users:student"},
					},
				],
				"namespace": "users",
				"permissions": [
					"read_first_name",
					"write_password",
					"export",
				],
				"relation": "AND",
			},
			{
				"appName": "OX",
				"conditions": [],
				"namespace": "mail",
				"permissions": [
					"edit-spam-filter",
					"export",
				],
				"relation": "AND",
			},
			{
				"appName": "radius",
				"conditions": [],
				"namespace": "wlan",
				"permissions": ["edit-access"],
				"relation": "AND",
			},
		],
		"ucsschool:users:student": [{
			"appName": "ucsschool",
			"conditions": [],
			"namespace": "users",
			"permissions": ["read_nickname"],
			"relation": "AND",
		}],
		"ucsschool:users:admin": [{
			"appName": "ucsschool",
			"conditions": [],
			"namespace": "users",
			"permissions": [
				"read_password",
				"write_password",
			],
			"relation": "AND",
		}],
	}
	inp = {
		"actor": {
			"id": "actor_id_1",
			#  The roles were choosen to show that we can return multiple roles
			#  while still filtering some (role ucsschool:users:student)
			"roles": {"ucsschool:users:teacher", "ucsschool:users:admin"},
		},
		"targets": [
			{
				"old": {"id": "target_id_1"},
				"new": {"id": "target_id_1"},
			},
			{
				"old": {"id": "target_id_2"},
				"new": {"id": "target_id_2"},
			},
		],
		#  The namespaces were chosen to show that we can return multiple apps and namespaces
		#  while still filtering apps (radius) and namespaces (namespace exams from app ucsschool)
		"namespaces": {"ucsschool": {"users", "groups"}, "OX": {"mail"}},
		"contexts": {},
		"extra_args": {},
	}
	result = get_permissions with input as inp
		with data.univention.mapping.roleCapabilityMapping as role_capability_mapping

	# regal ignore: print-or-trace-call
	print("TEST_DEBUG -- result: ", result)
	result == {
		{
			"target_id": "target_id_1",
			"permissions": {
				{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "read_last_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "write_password"},
				{"appName": "OX", "namespace": "mail", "permission": "edit-spam-filter"},
				{"appName": "OX", "namespace": "mail", "permission": "export"},
				{"appName": "ucsschool", "namespace": "groups", "permission": "read_display_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "read_password"},
			},
		},
		{
			"target_id": "target_id_2",
			"permissions": {
				{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "read_last_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "write_password"},
				{"appName": "OX", "namespace": "mail", "permission": "edit-spam-filter"},
				{"appName": "OX", "namespace": "mail", "permission": "export"},
				{"appName": "ucsschool", "namespace": "groups", "permission": "read_display_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "read_password"},
			},
		},
	}
}

test_get_permissions_empty_input if {
	inp = {}
	result = get_permissions with input as inp

	# regal ignore: print-or-trace-call
	print("TEST_DEBUG -- result: ", result)
	result == set()
}

test_get_permissions_wrong_role if {
	inp = {
		"actor": {
			"id": "actor_id_1",
			"roles": {"ucsschool:users:parent"},
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

	# regal ignore: print-or-trace-call
	print("TEST_DEBUG -- result: ", result)
	result == {{
		"target_id": "target_id_1",
		"permissions": set(),
	}}
}

check_permissions_parametrize := [
	{
		"input": {},
		"result": set(),
	},
	{
		"input": {
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
			"permissions": {{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"}},
		},
		"result": {{"target_id": "target_id_1", "result": true}},
	},
	{
		"input": {
			"actor": {
				"id": "actor_id_1",
				"roles": {"ucsschool:users:teacher"},
			},
			"targets": [{
				"old": {"id": "target_id_1"},
				"new": {"id": "target_id_1"},
			}],
			"namespaces": null,
			"contexts": {},
			"extra_args": {},
			"permissions": {{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"}},
		},
		"result": {{"target_id": "target_id_1", "result": true}},
	},
	{
		"input": {
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
			"permissions": {
				{"appName": "ucsschool", "namespace": "users", "permission": "read_first_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "read_last_name"},
				{"appName": "ucsschool", "namespace": "users", "permission": "write_password"},
				{"appName": "ucsschool", "namespace": "users", "permission": "export"},
			},
		},
		"result": {{"target_id": "target_id_1", "result": true}},
	},
	{
		"input": {
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
			"permissions": {{"appName": "ucsschool", "namespace": "users", "permission": "doesnotexist"}},
		},
		"result": {{"target_id": "target_id_1", "result": false}},
	},
]

test_check_permissions if {
	every case in check_permissions_parametrize {
		inp = case.input
		result := check_permissions with input as inp

		# regal ignore: print-or-trace-call
		print("TEST_DEBUG -- result: ", result)
		result == case.result
	}
}
