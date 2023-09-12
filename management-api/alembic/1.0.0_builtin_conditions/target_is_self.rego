package guardian.conditions

import future.keywords.if

condition("guardian:builtin:target_is_self", parameters, condition_data) if {
	parameters.field
	condition_data.actor.attributes[parameters.field] == condition_data.target.old.attributes[parameters.field]
} else if {
	not parameters.field
	condition_data.actor.id == condition_data.target.old.id
} else = false
