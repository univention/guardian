import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface ParameterResponseData {
  name: string;
}

export interface ConditionResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  resource_url: string;
  documentation: string;
  parameters: ParameterResponseData[];
}

export interface ConditionsResponse {
  pagination: PaginationResponseData;
  conditions: ConditionResponseData[];
}

export interface ConditionParameter {
  name: string;
}

export interface DisplayCondition {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
  documentation: string;
  parameters: ConditionParameter[];
}

export interface WrappedConditionsList {
  conditions: DisplayCondition[];
}
