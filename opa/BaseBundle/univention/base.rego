package univention.base

import future.keywords.contains
import future.keywords.if
import future.keywords.in

import data.univention.mapping.roleCapabilityMapping

# input.actor: The acting object
# input.targets: The list of target objects
# input.namespaces: Dictionary of app names to set of namespaces to return the permissions for
# input.contexts: The list of contexts provided to the request
# input.extra_args: Dictionary of additional arguments to pass to condition evaluation
# result: Set of dictionaries with target_id (string) and permissions (set of strings).
get_permissions contains result if {
	some target_object in input.targets
	permissions := {permission |
		some role in input.actor.roles
		some capability in roleCapabilityMapping[role]
		some app_name, namespaces in input.namespaces
		capability.appName == app_name
		some namespace in namespaces
		capability.namespace == namespace
		some permision_type in capability.permissions
		permission := {"appName": app_name, "namespace": namespace, "permission": permision_type}
	}
	result := {
		"target_id": target_object.old.id,
		"permissions": permissions,
	}
}
