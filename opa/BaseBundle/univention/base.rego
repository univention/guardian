package univention.base

import future.keywords.contains
import future.keywords.if
import future.keywords.in

import data.univention.mapping.roleCapabilityMapping

# input.actor: The acting object
# input.targets: The list of target objects
# input.namespaces: The list of namespaces to return the permissions for
# input.contexts: The list of contexts provided to the request
# input.extra_args: Dictionary of additional arguments to pass to condition evaluation
# result: Set of dictionaries with target_id (string) and permissions (set of strings).
get_permissions contains result if {
	some target_object in input.targets
	result := {
		"target_id": target_object.old.id,
		"permissions": set(),
	}
}
