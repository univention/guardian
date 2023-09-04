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
		some namespace in input.namespaces[appName]
		capability.appName == appName
		capability.namespace == namespace

		permission := {"appName": appName, "namespace": namespace, "permission": capability.permissions[_]}
	}
	result := {
		"target_id": target_object.old.id,
		"permissions": permissions,
	}
}
