package guardian.conditions

import future.keywords.if
import future.keywords.in

condition("guardian:builtin:target_has_role", parameters, condition_data) if {
	parameters.role in condition_data.target.old.roles
} else = false
