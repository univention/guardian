import type {
  CapabilityResponseData,
  CapabilitiesResponse,
  CapabilityConditionResponseData,
  CapabilityParameterResponseData,
  CapabilityPermissionResponseData,
} from '@/helpers/models/capabilities';
import type {PaginationResponseData} from '@/helpers/models/pagination';
import type {RoleResponseData} from '@/helpers/models/roles';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockRoles} from '@/helpers/mocks/api/roles';
import {makeMockConditions} from '@/helpers/mocks/api/conditions';
import {makeMockPermissions} from '@/helpers/mocks/api/permissions';

export const makeMockCapabilities = (): CapabilityResponseData[] => {
  const mockRoles = makeMockRoles();
  const mockConditions = makeMockConditions();
  const mockPermissions = makeMockPermissions();
  const numCapabilities: number = 3;

  const capabilities: CapabilityResponseData[] = [];
  mockRoles.forEach((role: RoleResponseData) => {
    for (let x = 1; x <= numCapabilities; x++) {
      const app = `app-${x}`;
      const namespace = `namespace-${x}`;

      let relation: 'AND' | 'OR' = 'AND';
      if (x % 2 === 0) {
        relation = 'OR';
      }

      const conditions: CapabilityConditionResponseData[] = [];
      for (let y = 1; y < x; y++) {
        const condition = mockConditions[Math.floor(Math.random() * mockConditions.length)];
        if (!condition) continue;
        const parameters: CapabilityParameterResponseData[] = [];
        condition.parameters.forEach(param => {
          parameters.push({
            name: param.name,
            value: `test-value-${y}`,
          });
        });

        conditions.push({
          app_name: condition.app_name,
          namespace_name: condition.namespace_name,
          name: condition.name,
          parameters: parameters,
        });
      }

      const capPermissions = mockPermissions
        .filter(perm => {
          return perm.app_name === app && perm.namespace_name === namespace;
        })
        .slice(x - 1);
      const permissions: CapabilityPermissionResponseData[] = [];
      capPermissions.forEach(perm => {
        permissions.push({
          app_name: perm.app_name,
          namespace_name: perm.namespace_name,
          name: perm.name,
        });
      });

      const id = `${role.app_name}-${role.namespace_name}-${role.name}`;

      capabilities.push({
        name: `capability-${id}`,
        display_name: `Capability for ${id}`,
        resource_url: `https://localhost/guardian/management/capability/app-${x}/namespace-${x}/capability-${x}`,
        app_name: app,
        namespace_name: namespace,
        role: role,
        conditions: conditions,
        relation: relation,
        permissions: permissions,
      });
    }
  });
  return capabilities;
};

export const makeMockCapabilitiesResponse = (capabilities: CapabilityResponseData[]): CapabilitiesResponse => {
  const pagination: PaginationResponseData = getPagination(capabilities.length);
  return {
    pagination: pagination,
    capabilities: capabilities,
  };
};
