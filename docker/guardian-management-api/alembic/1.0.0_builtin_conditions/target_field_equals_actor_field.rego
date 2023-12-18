package guardian.conditions

import future.keywords.if
import future.keywords.in

condition("guardian:builtin:target_field_equals_actor_field", parameters, condition_data) if {
	target_field_value := condition_data.target.old.attributes[parameters.target_field]
	actor_field_value := condition_data.actor.attributes[parameters.actor_field]
	target_field_value == actor_field_value
} else = false
