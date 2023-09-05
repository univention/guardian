package univention.utils_test

import data.univention.utils.evaluate_conditions
import future.keywords.every
import future.keywords.in

import data.univention.mapping.role_capability_mapping

#######################
# evaluate_conditions #
#######################

test_evaluate_conditions {
	evaluate_conditions("OR", [], {})
	not evaluate_conditions("OR", [{"name": "doesnotexist", "parameters": {}}], {})
	evaluate_conditions("AND", [], {})
	not evaluate_conditions("AND", [{"name": "doesnotexist", "parameters": {}}], {})
}

test_evaluate_conditions_integration {
	evaluate_conditions(
		"OR",
		[{"name": "only_if_param_result_true", "parameters": {"result": true}}],
		{},
	)
	not evaluate_conditions(
		"OR",
		[{"name": "only_if_param_result_true", "parameters": {"result": false}}],
		{},
	)
	evaluate_conditions(
		"OR",
		[
			{"name": "only_if_param_result_true", "parameters": {"result": true}},
			{"name": "doesnotexist", "parameters": {}},
		],
		{},
	)
	evaluate_conditions(
		"AND",
		[{"name": "only_if_param_result_true", "parameters": {"result": true}}],
		{},
	)
	not evaluate_conditions(
		"AND",
		[{"name": "only_if_param_result_true", "parameters": {"result": false}}],
		{},
	)
	not evaluate_conditions(
		"AND",
		[
			{"name": "only_if_param_result_true", "parameters": {"result": true}},
			{"name": "doesnotexist", "parameters": {}},
		],
		{},
	)
}
