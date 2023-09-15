package univention.utils_test

import future.keywords.every
import future.keywords.in

import data.univention.mapping.role_capability_mapping
import data.univention.utils.evaluate_conditions
import data.univention.utils.extract_role_and_context

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

############################
# extract_role_and_context #
############################

extract_role_and_context_parametrize := [
	{
		"input": "",
		"result": {
			"role": "",
			"context": null,
		},
	},
	{
		"input": null,
		"result": {
			"role": null,
			"context": null,
		},
	},
	{
		"input": "app_name:namespace:role&app_name:namespace:context",
		"result": {
			"role": "app_name:namespace:role",
			"context": "app_name:namespace:context",
		},
	},
	{
		"input": "role&context",
		"result": {
			"role": "role",
			"context": "context",
		},
	},
]

test_extract_role_and_context {
	every case in extract_role_and_context_parametrize {
		result := extract_role_and_context(case.input)

		# regal ignore: print-or-trace-call
		print("TEST_DEBUG result: ", result, " expected: ", case.result)
		result == case.result
	}
}
