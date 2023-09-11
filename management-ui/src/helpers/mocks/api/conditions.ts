import type {ConditionResponseData, ConditionsResponse, ParameterResponseData} from '@/helpers/models/conditions';
import type {PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockNamespaces} from '@/helpers/mocks/api/namespaces';

export const makeMockConditions = (): ConditionResponseData[] => {
  const namespaces = makeMockNamespaces();
  const numConditions: number = 5;

  const conditions: ConditionResponseData[] = [];
  namespaces.forEach(namespace => {
    for (let x = 1; x <= numConditions; x++) {
      const parameters: ParameterResponseData[] = [];
      for (let y = 1; y < x; y++) {
        parameters.push({name: `parameter_${y}`});
      }

      conditions.push({
        name: `condition-${x}`,
        display_name: `Condition ${x}`,
        resource_url: `https://localhost/guardian/management/conditions/${namespace.app_name}/${namespace.name}/condition-${x}`,
        app_name: `${namespace.app_name}`,
        namespace_name: `${namespace.name}`,
        documentation: `Some documentation for condition-${x}.`,
        parameters: parameters,
      });
    }
  });
  return conditions;
};

export const makeMockConditionsResponse = (conditions: ConditionResponseData[]): ConditionsResponse => {
  const pagination: PaginationResponseData = getPagination(conditions.length);
  return {
    pagination: pagination,
    conditions: conditions,
  };
};
