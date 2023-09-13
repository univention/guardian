interface Parameter {
  name: string;
}

export interface DisplayCondition {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
  documentation: string;
  parameters: Parameter[];
}

export interface WrappedConditionsList {
  conditions: DisplayCondition[];
}
