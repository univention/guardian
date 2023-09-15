import type {ListResponseModel} from '@/helpers/models';
import {rolesListResponseModel} from '@/helpers/mocks/roles';
import {namespacesListResponseModel} from '@/helpers/mocks/namespaces';
import {contextsListResponseModel} from '@/helpers/mocks/contexts';
import {capabilitiesListResponseModel} from '@/helpers/mocks/capabilities';

export const fetchMockData = <T>(mockData: T, name: string): Promise<T> => {
  console.debug(`${name}. VITE_USE_REAL_BACKEND===false in DEV mode. Returning mock data:`, mockData);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockData);
    }, 1000);
  });
};

export const getRolesListResponseModels = (): ListResponseModel[] => {
  const rows: ListResponseModel[] = [];

  for (let x = 2; x < 500; x++) {
    const y = JSON.parse(JSON.stringify(rolesListResponseModel));
    y.id = `role${x}.foo`;
    y.attributes.name.value = y.id;
    y.attributes.displayname.value = `Role ${x}`;
    y.attributes.app.value = 'App1';
    y.attributes.namespace.value = 'Namespace1';
    if (x % 2 === 0) {
      y.allowedActions = ['edit'];
    }
    rows.push(y);
  }
  return rows;
};
export const getNamespacesListResponseModels = (): ListResponseModel[] => {
  const rows: ListResponseModel[] = [];

  for (let x = 2; x < 500; x++) {
    const y = JSON.parse(JSON.stringify(namespacesListResponseModel));
    y.id = `namespace${x}`;
    y.attributes.name.value = y.id;
    y.attributes.displayname.value = `Namespace ${x}`;
    y.attributes.app.value = 'App1';
    if (x % 2 === 0) {
      y.allowedActions = ['edit'];
    }
    rows.push(y);
  }
  return rows;
};
export const getContextsListResponseModels = (): ListResponseModel[] => {
  const rows: ListResponseModel[] = [];

  for (let x = 2; x < 500; x++) {
    const y = JSON.parse(JSON.stringify(contextsListResponseModel));
    y.id = `context${x}`;
    y.attributes.name.value = y.id;
    y.attributes.displayname.value = `Context ${x}`;
    y.attributes.app.value = 'App1';
    y.attributes.namespace.value = 'Namespace1';
    if (x % 2 === 0) {
      y.allowedActions = ['edit'];
    }
    rows.push(y);
  }
  return rows;
};
export const getCapabilitiesListResponseModels = (): ListResponseModel[] => {
  const rows: ListResponseModel[] = [];

  for (let x = 2; x < 500; x++) {
    const y = JSON.parse(JSON.stringify(capabilitiesListResponseModel));
    y.id = `capability${x}`;
    y.attributes.name.value = y.id;
    y.attributes.displayname.value = `Capability ${x}`;
    y.attributes.app.value = 'App1';
    y.attributes.namespace.value = 'Namespace1';
    if (x % 2 === 0) {
      y.allowedActions = ['edit'];
    }
    rows.push(y);
  }
  return rows;
};
