import {type ContextResponseData, type ContextsResponse} from '@/helpers/models/contexts';
import {type PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';
import {makeMockNamespaces} from '@/helpers/mocks/api/namespaces';

export const makeMockContexts = (): ContextResponseData[] => {
  const namespaces = makeMockNamespaces();
  const numContexts: number = 5;
  const contexts: ContextResponseData[] = [];
  namespaces.forEach(namespace => {
    for (let x = 1; x <= numContexts; x++) {
      contexts.push({
        name: `context-${x}`,
        display_name: `Context ${x}`,
        resource_url: `https://localhost/guardian/management/contexts/${namespace.app_name}/${namespace.name}/context-${x}`,
        app_name: `${namespace.app_name}`,
        namespace_name: `${namespace.name}`,
      });
    }
  });
  return contexts;
};

export const makeMockContextsResponse = (contexts: ContextResponseData[]): ContextsResponse => {
  const pagination: PaginationResponseData = getPagination(contexts.length);
  return {
    pagination: pagination,
    contexts: contexts,
  };
};
