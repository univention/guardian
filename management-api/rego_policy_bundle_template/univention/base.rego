package univention.base

import future.keywords.contains
import future.keywords.every
import future.keywords.if
import future.keywords.in

import data.guardian.mapping.roleCapabilityMapping
import data.univention.utils.evaluate_conditions
import data.univention.utils.extract_role_and_context
import data.univention.utils.extract_target_id

# check if a dictionary of app to namespaces contains a given namespace
# for the given app
# namespaces: Dictionary of app names to set of namespaces
# app_name: The app name to check
# namespace: The namespace to check
# result: Boolean indicating whether the namespace is contained in the set of namespaces
has_namespace(namespaces, app_name, namespace) if {
	namespace in namespaces[app_name]
} else = false

# actor: The acting object
# roleCapabilityMapping: Dictionary of role names to set of capabilities
# namespaces: Dictionary of app names to set of namespaces to return the permissions for
# contexts: The list of contexts provided to the request
# extra_args: Dictionary of additional arguments to pass to condition evaluation
# result: Set of permission objects
_get_permissions(actor, target_object, roleCapabilityMapping, namespaces, contexts, extra_args) := {permission |
	some role in actor.roles
	role_and_context := extract_role_and_context(role)
	role_name := role_and_context.role
	role_context := role_and_context.context
	some capability in roleCapabilityMapping[role_name]
	app_name := capability.appName
	namespace := capability.namespace
	any([is_null(namespaces), has_namespace(namespaces, app_name, namespace)])
	condition_data := {
		"actor": actor,
		"actor_role": role_and_context,
		"target": {
			"old": target_object.old,
			"new": target_object.new,
		},
		"namespaces": namespaces,
		"contexts": contexts,
		"extra_args": extra_args,
	}
	evaluate_conditions(capability.relation, capability.conditions, condition_data)
	some permission_type in capability.permissions
	permission := {"appName": app_name, "namespace": namespace, "permission": permission_type}
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
	permissions := _get_permissions(
		input.actor,
		target_object,
		roleCapabilityMapping,
		input.namespaces,
		input.contexts,
		input.extra_args,
	)

	result := {
		"target_id": extract_target_id(target_object),
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
	permissions := _get_permissions(
		input.actor,
		target_object,
		roleCapabilityMapping,
		input.namespaces,
		input.contexts,
		input.extra_args,
	)
	has_all_permissions := all([
		is_null(input.permissions) == false,
		object.subset(permissions, {permission | some permission in input.permissions}),
	])

	result := {
		"target_id": extract_target_id(target_object),
		"result": has_all_permissions,
	}
}
