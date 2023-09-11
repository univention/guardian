import {type NamespaceResponseData, type NamespacesResponse} from '@/helpers/models/namespaces';
import {type PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockApps} from '@/helpers/mocks/api/apps';

export const makeMockNamespaces = (): NamespaceResponseData[] => {
  const apps = makeMockApps();
  const numNamespaces: number = 3;
  const namespaces: NamespaceResponseData[] = [];
  apps.forEach(app => {
    for (let x = 1; x <= numNamespaces; x++) {
      namespaces.push({
        name: `namespace-${x}`,
        display_name: `Namespace ${x}`,
        resource_url: `https://localhost/guardian/management/namespaces/${app.name}/namespace-${x}`,
        app_name: `${app.name}`,
      });
    }
  });
  return namespaces;
};

export const makeMockNamespacesResponse = (namespaces: NamespaceResponseData[]): NamespacesResponse => {
  const pagination: PaginationResponseData = getPagination(namespaces.length);
  return {
    pagination: pagination,
    namespaces: namespaces,
  };
};
