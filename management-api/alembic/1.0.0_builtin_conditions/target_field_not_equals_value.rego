package guardian.conditions

import future.keywords.if
import future.keywords.in

condition("guardian:builtin:target_field_not_equals_value", parameters, condition_data) if {
	condition_data.target.old.attributes[parameters.field] != parameters.value
} else = false
