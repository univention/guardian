import {type PermissionResponseData, type PermissionsResponse} from '@/helpers/models/permissions';
import {type PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockNamespaces} from '@/helpers/mocks/api/namespaces';

export const makeMockPermissions = (): PermissionResponseData[] => {
  const namespaces = makeMockNamespaces();
  const numPermissions: number = 5;
  const permissions: PermissionResponseData[] = [];
  namespaces.forEach(namespace => {
    for (let x = 1; x <= numPermissions; x++) {
      permissions.push({
        name: `permission-${x}`,
        display_name: `Permission ${x}`,
        resource_url: `https://localhost/guardian/management/permissions/${namespace.app_name}/${namespace.name}/permission-${x}`,
        app_name: `${namespace.app_name}`,
        namespace_name: `${namespace.name}`,
      });
    }
  });
  return permissions;
};

export const makeMockPermissionsResponse = (permissions: PermissionResponseData[]): PermissionsResponse => {
  const pagination: PaginationResponseData = getPagination(permissions.length);
  return {
    pagination: pagination,
    permissions: permissions,
  };
};
