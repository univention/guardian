package guardian.conditions

import future.keywords.if
import future.keywords.in

import data.univention.utils.extract_role_and_context

condition("guardian:builtin:target_has_role_in_same_context", parameters, condition_data) if {
	actor_context := condition_data.actor_role.context
	some target_crole in condition_data.target.old.roles
	target_role_and_context := extract_role_and_context(target_crole)
	actor_context == target_role_and_context.context
	parameters.role == target_role_and_context.role
} else = false
