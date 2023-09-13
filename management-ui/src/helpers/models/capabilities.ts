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
