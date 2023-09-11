import {type RoleResponseData, type RolesResponse} from '@/helpers/models/roles';
import {type PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockNamespaces} from '@/helpers/mocks/api/namespaces';

export const makeMockRoles = (): RoleResponseData[] => {
  const namespaces = makeMockNamespaces();
  const numRoles: number = 5;
  const roles: RoleResponseData[] = [];
  namespaces.forEach(namespace => {
    for (let x = 1; x <= numRoles; x++) {
      roles.push({
        name: `role-${x}`,
        display_name: `Role ${x}`,
        resource_url: `https://localhost/guardian/management/roles/${namespace.app_name}/${namespace.name}/role-${x}`,
        app_name: `${namespace.app_name}`,
        namespace_name: `${namespace.name}`,
      });
    }
  });
  return roles;
};

export const makeMockRolesResponse = (roles: RoleResponseData[]): RolesResponse => {
  const pagination: PaginationResponseData = getPagination(roles.length);
  return {
    pagination: pagination,
    roles: roles,
  };
};
