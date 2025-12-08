package guardian.conditions

import future.keywords.if
import future.keywords.in

condition("guardian:builtin:actor_field_equals_value", parameters, condition_data) if {
	condition_data.actor.attributes[parameters.field] == parameters.value
} else = false
