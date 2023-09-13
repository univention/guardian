package univention.utils

import future.keywords.every
import future.keywords.if
import future.keywords.in

import data.guardian.conditions.condition

evaluate_conditions("AND", conditions, condition_data) if {
	every c in conditions {
		condition(c.name, c.parameters, condition_data)
	}
}

evaluate_conditions("OR", conditions, condition_data) if {
	some c in conditions
	condition(c.name, c.parameters, condition_data)
}

evaluate_conditions("OR", conditions, condition_data) if {
	conditions == []
}
