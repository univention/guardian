import type {
  ListResponseModel,
  AddViewConfig,
  FormValues,
  ObjectType,
  DetailResponseModel,
  ListViewConfigs,
  LabeledValue,
} from '@/helpers/models';
// eslint-disable-next-line
import {fetchAuthenticated} from '@/helpers/retrieveData';
// eslint-disable-next-line
import {useErrorStore} from '@/stores/error';
import i18next from 'i18next';
import {
  listViewConfig,
  addRoleViewConfig,
  addContextViewConfig,
  addNamespaceViewConfig,
  addCapabilityViewConfig,
  roleDetailResponseModel,
  namespaceDetailResponseModel,
  contextDetailResponseModel,
  capabilityDetailResponseModel,
  fetchMockData,
  getRolesListResponseModels,
  getNamespacesListResponseModels,
  getCapabilitiesListResponseModels,
  getContextsListResponseModels,
} from '@/helpers/mocks';

const needMock = import.meta.env.VITE_USE_REAL_BACKEND !== 'true';

const getError = async (response: Response): Promise<{detail: unknown} | null> => {
  if (!response.ok) {
    const text = (await response.text()) || response.statusText;
    let detail = {
      detail: text,
    };
    try {
      const json = JSON.parse(text);
      if (json && typeof json === 'object' && 'detail' in json) {
        detail = json;
      }
    } catch (err) {
      // Either not a JSON response, or unparsable. We'll just ignore this.
    }
    return detail;
  }
  return null;
};

export const fetchListViewConfig = async (): Promise<ListViewConfigs> => {
  if (needMock) {
    return fetchMockData(listViewConfig, 'fetchListViewConfig');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData(listViewConfig, 'fetchListViewConfig');

  /*
  const answer = await fetchAuthenticated('/ucsschool/guardian/v1/pageconf/listView');
  const error = await getError(answer);
  if (error) {
    const errorStore = useErrorStore();
    const title = i18next.t(`dataAccess.fetchListViewConfig.error.title`);
    errorStore.push({
      title,
      message: JSON.stringify(error.detail),
      unRecoverable: true,
    });
    return Promise.reject(answer);
  }
  return await answer.json();
  */
};

export const fetchAddViewConfig = async (objectType: ObjectType): Promise<AddViewConfig> => {
  if (needMock) {
    const config = {
      role: addRoleViewConfig,
      context: addContextViewConfig,
      namespace: addNamespaceViewConfig,
      capability: addCapabilityViewConfig,
    }[objectType];
    return fetchMockData(config, 'fetchAddViewConfig');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  const config = {
    role: addRoleViewConfig,
    context: addContextViewConfig,
    namespace: addNamespaceViewConfig,
    capability: addCapabilityViewConfig,
  }[objectType];
  return fetchMockData(config, 'fetchAddViewConfig');
  /*
  const answer = await fetchAuthenticated(`/ucsschool/guardian/v1/pageconf/addView${objectType}`);
  const error = await getError(answer);
  if (error) {
    const errorStore = useErrorStore();
    const title = i18next.t('dataAccess.fetchListViewConfig.error.title');
    errorStore.push({
      title,
      message: JSON.stringify(error.detail),
    });
    return Promise.reject(answer);
  }

  return await answer.json();
  */
};

export const fetchObjects = async (
  objectType: ObjectType,
  // eslint-disable-next-line
  values: FormValues,
  // eslint-disable-next-line
  limit?: number
): Promise<ListResponseModel[] | null> => {
  if (needMock) {
    const mockData = {
      role: getRolesListResponseModels,
      context: getContextsListResponseModels,
      namespace: getNamespacesListResponseModels,
      capability: getCapabilitiesListResponseModels,
    }[objectType]();
    return fetchMockData(mockData, 'fetchObjects');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  const mockData = {
    role: getRolesListResponseModels,
    context: getContextsListResponseModels,
    namespace: getNamespacesListResponseModels,
    capability: getCapabilitiesListResponseModels,
  }[objectType]();
  return fetchMockData(mockData, 'fetchObjects');

  /*
  const urlSearchParams = new URLSearchParams({});
  // TODO add `values` argument to urlSearchParams
  if (limit) {
    urlSearchParams.append('limit', `${limit}`);
  }

  const answer = await fetchAuthenticated(`/ucsschool/guardian/v1/${objectType}?${urlSearchParams.toString()}`);
  const error = await getError(answer);
  if (error) {
    if (typeof error.detail === 'object' && error.detail !== null && 'type' in error.detail) {
      const detail = error.detail as {type: string};
      if (detail.type === 'SearchLimitReached') {
        return null;
      }
    }
    const errorStore = useErrorStore();
    const title = i18next.t('dataAccess.fetchObjects.error.title');
    errorStore.push({
      title,
      message: JSON.stringify(error.detail),
    });
    return Promise.reject(answer);
  }
  return await answer.json();
  */
};

export const fetchObject = async (
  objectType: ObjectType,
  // eslint-disable-next-line
  id: string
): Promise<DetailResponseModel | null> => {
  if (needMock) {
    const model = {
      role: roleDetailResponseModel,
      context: contextDetailResponseModel,
      namespace: namespaceDetailResponseModel,
      capability: capabilityDetailResponseModel,
    }[objectType];
    return fetchMockData(model, 'fetchObject');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  const model = {
    role: roleDetailResponseModel,
    context: contextDetailResponseModel,
    namespace: namespaceDetailResponseModel,
    capability: capabilityDetailResponseModel,
  }[objectType];
  return fetchMockData(model, 'fetchObject');

  /*
  const answer = await fetchAuthenticated(`/ucsschool/guardian/v1/${objectType}/${id}`);
  if (answer.status === 404) {
    return null;
  }
  return await answer.json();
  */
};

export type SaveError =
  | {
      type: 'generic';
      message: string;
    }
  | {
      type: 'fieldErrors';
      errors: {
        field: string;
        message: string;
      }[];
    };

type SaveContext =
  | 'updaterole'
  | 'createrole'
  | 'updatecontext'
  | 'createcontext'
  | 'updatenamespace'
  | 'createnamespace';
// eslint-disable-next-line
const getSaveError = async (response: Response, context: SaveContext): Promise<SaveError | null> => {
  const errorJson = await getError(response);
  if (!errorJson) {
    return null;
  }
  if (response.status === 422) {
    // FIXME validate against json.schema
    if (Array.isArray(errorJson.detail)) {
      const detail: {loc: string[]; msg: string; type: string}[] = errorJson.detail;
      const error: SaveError = {
        type: 'fieldErrors',
        errors: [],
      };
      for (const iDetail of detail) {
        const field = iDetail.loc[iDetail.loc.length - 1];
        if (field) {
          error.errors.push({
            field,
            message: iDetail.msg,
          });
        }
      }
      return error;
    }
  }
  if (response.status === 404) {
    return {
      type: 'generic',
      message: i18next.t(`dataAccess.${context}.error.404`),
    };
  }
  return {
    type: 'generic',
    message: String(errorJson.detail),
  };
};
export const updateObject = async (
  // eslint-disable-next-line
  objectType: ObjectType,
  // eslint-disable-next-line
  url: string,
  // eslint-disable-next-line
  values: FormValues
): Promise<SaveError | null> => {
  if (needMock) {
    /*
    return fetchMockData({
      type: 'fieldErrors',
      errors: [
        {
          field: 'password',
          message: 'This should be overwritten in EditView',
        },
      ],
    }, 'updateUser');
    */
    return fetchMockData(null, 'updateObject');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData(null, 'updateObject');

  /*
  const fixedProtocolUrl = url.replace(/https?:/, location.protocol);
  const answer = await fetchAuthenticated(`${fixedProtocolUrl}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  });
  return await getSaveError(answer, `update${objectType}`);
  */
};

interface CreateObjectSuccess {
  status: 'success';
  name: string;
}
interface CreateObjectError {
  status: 'error';
  error: SaveError;
}
type CreateObjectResponse = CreateObjectSuccess | CreateObjectError;
export const createObject = async (
  objectType: ObjectType,
  // eslint-disable-next-line
  values: FormValues
): Promise<CreateObjectResponse> => {
  if (needMock) {
    return {
      status: 'success',
      name: objectType,
    };
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return {
    status: 'success',
    name: objectType,
  };

  /*
  const answer = await fetchAuthenticated(`/ucsschool/guardian/v1/${objectType}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  });

  const error = await getSaveError(answer, `create${objectType}`);
  if (error) {
    return {
      status: 'error',
      error,
    };
  }

  return {
    status: 'success',
    name: values['name'] as string,
  };
  */
};

export const deleteCapabilities = async(ids: string[]): Promise<{id: string; error: string}[]> => {
  if (needMock) {
    return fetchMockData([
      {
        id: ids[0] as string,
        error: 'some error',
      },
    ], 'deleteCapabilities');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData([
    {
      id: ids[0] as string,
      error: 'some error',
    },
  ], 'deleteCapabilities');

  /*
  const responses = await Promise.all(ids.map(id => fetchAuthenticated(`/ucsschool/guardian/v1/capabilities/${id}`, {
    method: 'DELETE',
  })));
  const errors = await Promise.all(responses.map(x => getError(x)));
  const fails: {id: string; error: string}[] = [];
  for (let x = 0; x < responses.length; x++) {
    const error = errors[x];
    if (error) {
      fails.push({
        id: ids[x] as string,
        error: JSON.stringify(error.detail),
      });
    }
  }
  return fails;
  */
};


const fetchNamespacesMock = (appName: string): LabeledValue<string>[] => {
  const mock: LabeledValue<string>[] = [];
  for (let x = 0; x < 2; x++) {
    mock.push({
      label: `${appName}/Namespace ${x + 1}`,
      value: `${appName}/namespace${x + 1}`,
    });
  }
  return mock;
};
export const fetchNamespaces = async (appName: string): Promise<LabeledValue<string>[]> => {
  if (needMock) {
    return fetchMockData(fetchNamespacesMock(appName), 'fetchNamespaces');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData(fetchNamespacesMock(appName), 'fetchNamespaces');
};

const fetchPermissionsMock = (appName: string, namespaceName: string): LabeledValue<string>[] => {
  const mock: LabeledValue<string>[] = [];
  for (let x = 0; x < 2; x++) {
    mock.push({
      label: `${appName}/${namespaceName}/Permission ${x + 1}`,
      value: `${appName}/${namespaceName}/permission${x + 1}`,
    });
  }
  return mock;
};
export const fetchPermissions = async (appName: string, namespaceName: string): Promise<LabeledValue<string>[]> => {
  if (needMock) {
    return fetchMockData(fetchPermissionsMock(appName, namespaceName), 'fetchNamespaces');
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData(fetchPermissionsMock(appName, namespaceName), 'fetchNamespaces');
};