package guardian.conditions

import future.keywords.every
import future.keywords.if
import future.keywords.in

# CONDITION DATA
# This is the data that is passed to the condition
# condition_data = {
#         "actor": {},
#         "actor_role": {},
#         "target": {
#              "old": {},
#              "new": {},
#         },
#         "namespaces": {},
#         "contexts": set(),
#         "extra_args": {},
#         "parameters": {},
# }

# This condition evaluates to true only if the parameter "result" is true
condition("only_if_param_result_true", parameters, condition_data) if {
	parameters.result == true
} else = false
