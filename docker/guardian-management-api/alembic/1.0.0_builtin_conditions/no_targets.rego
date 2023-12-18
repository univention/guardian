package guardian.conditions

import future.keywords.if

condition("guardian:builtin:no_targets", parameters, condition_data) if {
	condition_data.target.old.id == ""
	condition_data.target.new.id == ""
} else if {
	is_null(condition_data.target.old)
	is_null(condition_data.target.new)
} else if {
	condition_data.target.old == {}
	condition_data.target.new == {}
} else = false
