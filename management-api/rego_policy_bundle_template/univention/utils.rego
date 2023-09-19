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

# role_string: in the format "app_name:namespace:role&app_name:namespace:context"
# result: dict with keys "role" and "context"
extract_role_and_context(role_string) := result if {
	contains(role_string, "&")
	role_and_context := split(role_string, "&")
	result := {"role": role_and_context[0], "context": role_and_context[1]}
} else := {"role": role_string, "context": null}

# target_object: one of the objects as sent in input.targets
# result: the id of the target. Chosen in order from: old.id, new.id,
extract_target_id(target_object) := target_object.old.id if {
	target_object.old.id
} else := target_object.new.id if {
	target_object.new.id
} else := uuid.rfc4122(json.marshal(target_object))
