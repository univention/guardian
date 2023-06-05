package univention.base

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# input.actor: The acting object
# input.targets: The list of target objects
# input.namespaces: The list of namespaces to return the permissions for
# input.contexts: The list of contexts provided to the request
# input.extra_args: Dictionary of additional arguments to pass to condition evaluation
get_permissions contains result if {
    some target_object in input.targets
    result := {
        "target_id": target_object.id,
        "permissions": []
    }
}