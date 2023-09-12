package guardian.conditions

import future.keywords.if
import future.keywords.in

condition("guardian:builtin:actor_does_not_have_role", parameters, condition_data) if {
	not parameters.role in condition_data.actor.roles
} else = false
