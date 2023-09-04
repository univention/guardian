package univention.base

import future.keywords.contains
import future.keywords.every
import future.keywords.if
import future.keywords.in

import data.univention.mapping.roleCapabilityMapping

# roles: The list of actor roles
# roleCapabilityMapping: Dictionary of role names to set of capabilities
# namespaces: Dictionary of app names to set of namespaces to return the permissions for
# contexts: The list of contexts provided to the request
# extra_args: Dictionary of additional arguments to pass to condition evaluation
# result: Set of permission objects
_get_permissions(roles, target_object, roleCapabilityMapping, namespaces, contexts, extra_args) := permissions if {
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
}

# input.actor: The acting object
# input.targets: The list of target objects
# input.namespaces: Dictionary of app names to set of namespaces to return the permissions for
# input.contexts: The list of contexts provided to the request
# input.extra_args: Dictionary of additional arguments to pass to condition evaluation
# result: Set of dictionaries with target_id (string) and permissions (set of permission objects).
# regal ignore:avoid-get-and-list-prefix
get_permissions contains result if {
	some target_object in input.targets
	permissions := _get_permissions(input.actor.roles, target_object, roleCapabilityMapping, input.namespaces, input.contexts, input.extra_args)

	result := {
		"target_id": target_object.old.id,
		"permissions": permissions,
	}
}

# input.actor: The acting object
# input.targets: The list of target objects
# input.namespaces: Dictionary of app names to set of namespaces to return the permissions for
# input.contexts: The list of contexts provided to the request
# input.extra_args: Dictionary of additional arguments to pass to condition evaluation
# input.permissions: Set of permission objects to check for
# result: List of objects indicating whether the actor has all given permissions for each of the targets.
check_permissions contains result if {
	input.targets
	some target_object in input.targets
	permissions := _get_permissions(input.actor.roles, target_object, roleCapabilityMapping, input.namespaces, input.contexts, input.extra_args)
	has_all_permissions := object.subset(permissions, {permission | some permission in input.permissions})

	result := {
		"target_id": target_object.old.id,
		"result": has_all_permissions,
	}
}
