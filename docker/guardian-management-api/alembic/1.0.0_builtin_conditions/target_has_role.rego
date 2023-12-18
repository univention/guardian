package guardian.conditions

import future.keywords.if
import future.keywords.in

import data.univention.utils.extract_role_and_context

condition("guardian:builtin:target_has_role", parameters, condition_data) if {
	some crole in condition_data.target.old.roles
	role_and_context := extract_role_and_context(crole)
	role_name := role_and_context.role
	role_name == parameters.role
} else = false
