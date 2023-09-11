import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface CapabilityRoleRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
}

export interface CapabilityRoleResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
}

export interface CapabilityParameterRequestData {
  name: string;
  value: string;
}

export interface CapabilityParameterResponseData {
  name: string;
  value: string;
}

export interface CapabilityConditionRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
  parameters: CapabilityParameterRequestData[];
}

export interface CapabilityConditionResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  parameters: CapabilityParameterResponseData[];
}

export interface CapabilityPermissionRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
}

export interface CapabilityPermissionResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
}

export interface NewCapabilityRequestData {
  app_name: string;
  namespace_name: string;
  name?: string;
  display_name: string;
  role: CapabilityRoleRequestData;
  conditions: CapabilityConditionRequestData[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermissionRequestData[];
}

export interface CapabilityRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  role: CapabilityRoleRequestData;
  conditions: CapabilityConditionRequestData[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermissionRequestData[];
}

export interface CapabilityResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  resource_url: string;
  role: CapabilityRoleResponseData;
  conditions: CapabilityConditionResponseData[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermissionResponseData[];
}

export interface CapabilityResponse {
  capability: CapabilityResponseData;
}

export interface CapabilitiesResponse {
  pagination: PaginationResponseData;
  capabilities: CapabilityResponseData[];
}

export interface CapabilityRole {
  appName: string;
  namespaceName: string;
  name: string;
}

export interface CapabilityParameter {
  name: string;
  value: string;
}

export interface CapabilityCondition {
  appName: string;
  namespaceName: string;
  name: string;
  parameters: CapabilityParameter[];
}

export interface CapabilityPermission {
  appName: string;
  namespaceName: string;
  name: string;
}

export interface Capability {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  role: CapabilityRole;
  conditions: CapabilityCondition[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermission[];
}

export interface NewCapability {
  appName: string;
  namespaceName: string;
  name?: string;
  displayName: string;
  role: CapabilityRole;
  conditions: CapabilityCondition[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermission[];
}

export interface DisplayCapability {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  role: CapabilityRole;
  conditions: CapabilityCondition[];
  relation: 'AND' | 'OR';
  permissions: CapabilityPermission[];
  resourceUrl: string;
}

export interface WrappedCapability {
  capability: DisplayCapability;
}

export interface WrappedCapabilitiesList {
  capabilities: DisplayCapability[];
}
