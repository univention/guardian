{{/*
Object name reproducing the pre-rename chart name "guardian-cerbos"
(univention/dev/projects/authorization-engine/guardian#290): a "cerbos"
suffix on the ordinary common.names.fullname, the same way e.g.
provisioning's udm-transformer Deployment suffixes its own fullname.
*/}}
{{- define "guardian.fullname" -}}
{{- printf "%s-cerbos" (include "common.names.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
