import type {
  AddViewConfig,
  DetailResponseModel,
  FormValues,
  LabeledValue,
  ListResponseModel,
  ListViewConfigs,
  ObjectType,
} from '@/helpers/models';
import i18next from 'i18next';
import {
  fetchMockData,
} from '@/helpers/mocks';
import {
  capabilityDetailResponseModel,
  contextDetailResponseModel,
  roleDetailResponseModel,
  namespaceDetailResponseModel,
  listViewConfig,
  addRoleViewConfig,
  addContextViewConfig,
  addNamespaceViewConfig,
  addCapabilityViewConfig,
} from '@/helpers/configs';
import {useSettingsStore} from '@/stores/settings';
import {useAdapterStore} from '@/stores/adapter';
import type {WrappedAppsList} from '@/helpers/models/apps';
import type {WrappedNamespacesList} from '@/helpers/models/namespaces';
import type {WrappedRolesList} from '@/helpers/models/roles';
import type {WrappedContextsList} from '@/helpers/models/contexts';
import type {WrappedCapabilitiesList} from '@/helpers/models/capabilities';
import type {WrappedRole} from '@/helpers/models/roles';
import type {WrappedNamespace} from '@/helpers/models/namespaces';
import type {WrappedContext} from '@/helpers/models/contexts';
import type {WrappedCapability} from '@/helpers/models/capabilities';
import type {WrappedPermissionsList} from '@/helpers/models/permissions';
import type {WrappedConditionsList} from '@/helpers/models/conditions';
import {SubElement, SubElementProps} from '@univention/univention-veb';
import type {Option} from '@univention/univention-veb/dist/types/components/form/elements/UComboBox.vue';

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

const fetchAppsOptions = async (withAllOption: boolean): Promise<LabeledValue<string>[]> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const apps: WrappedAppsList = await adapterStore.dataAdapter.fetchApps();
  const appsOptions = apps.apps.map(app => ({
    value: app.name,
    label: app.displayName || app.name,
  }));
  if (withAllOption) {
    appsOptions.unshift({
      label: 'All',
      value: '',
    });
  }

  return appsOptions;
}
const fetchConditionSubElement = async (): Promise<SubElementProps[]> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const conditions: WrappedConditionsList = await adapterStore.dataAdapter.fetchConditions();

  let extensions: Record<string, any[]> = {};
  let options: Option[] = [];


  conditions.conditions.forEach(condition => {
    const conditionId = `${condition.appName}:${condition.namespaceName}:${condition.name}`;

    if (condition.parameters.length > 0) {
      let inputs: {type: any; props: any}[] = [];
      condition.parameters.forEach(param => {
        inputs.push({
          type: SubElement.UInputText,
          props: {
            label: `${param.name}`,
            name: `${conditionId}-${param.name}`,
            required: true,
          },
        });
      });
      extensions[conditionId] = inputs;
    }

    options.push({
      label: conditionId,
      value: `${conditionId}`,
    });
  });

  return [
    {
      type: SubElement.UExtendingInput,
      props: {
        name: 'conditions',
        extensions: extensions,
        rootElement: {
          type: SubElement.UComboBox,
          props: {
            name: 'condition',
            label: 'Condition',
            options: options,
          },
        },
      },
    },
  ];
};

export const fetchListViewConfig = async (): Promise<ListViewConfigs> => {
  const appsOptions = await fetchAppsOptions(true);

  const config = JSON.parse(JSON.stringify(listViewConfig));
  for (const role of ['role', 'capability', 'namespace', 'context']) {
    const appField = config[role].searchForm.find(f => f.props.name === 'appSelection');
    appField.props.options = appsOptions;
  }

  return config;
};

export const fetchAddViewConfig = async (objectType: ObjectType): Promise<AddViewConfig> => {
  const appsOptions = await fetchAppsOptions(false);

  const config = {
    role: addRoleViewConfig,
    context: addContextViewConfig,
    namespace: addNamespaceViewConfig,
    capability: addCapabilityViewConfig,
  }[objectType];

  switch (objectType) {
    case 'role':
    case 'namespace':
    case 'context':
      config.pages[0].fieldsets[0].rows[0][0].props.options = appsOptions;
      break;
    case 'capability':
      config.pages[0].fieldsets[0].rows[0][0].props.options = appsOptions;
      const conditions = await fetchConditionSubElement();
      config.pages[0].fieldsets[0].rows[2][0].props.subElements = conditions;
      break;
    default:
      break;
  }

  return config;
};

export const fetchObjects = async (
  objectType: ObjectType,
  values: FormValues,
  id: string,
  // eslint-disable-next-line
  limit?: number
): Promise<ListResponseModel[] | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  console.log('values: ', values);
  console.log(objectType);
  console.log('id: ', id);
  switch (objectType) {
    case 'role': {
      function getId(url: string): string {
        const split = url.split('/');
        return `${split[split.length - 3]}:${split[split.length - 2]}:${split[split.length - 1]}`
      }
      const data: WrappedRolesList = await adapterStore.dataAdapter.fetchRoles(values.appSelection, values.namespaceSelection);
      return data.roles.map(role => ({
        id: getId(role.resourceUrl),
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: role.name,
            access: 'read',
          },
          displayname: {
            value: role.displayName,
            access: 'read',
          },
          app: {
            value: role.appName,
            access: 'read',
          },
          namespace: {
            value: role.namespaceName,
            access: 'read',
          },
        },
      }));
    }
    case 'namespace': {
      function getId(url: string): string {
        const split = url.split('/');
        return `${split[split.length - 2]}:${split[split.length - 1]}`
      }
      const data: WrappedNamespacesList = await adapterStore.dataAdapter.fetchNamespaces(values.appSelection);
      return data.namespaces.map(namespace => ({
        id: getId(namespace.resourceUrl),
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: namespace.name,
            access: 'read',
          },
          displayname: {
            value: namespace.displayName,
            access: 'read',
          },
          app: {
            value: namespace.appName,
            access: 'read',
          },
        },
      }));
    }
    case 'context': {
      function getId(url: string): string {
        const split = url.split('/');
        return `${split[split.length - 3]}:${split[split.length - 2]}:${split[split.length - 1]}`
      }
      const data: WrappedContextsList = await adapterStore.dataAdapter.fetchContexts(values.appSelection, values.namespaceSelection);
      return data.contexts.map(context => ({
        id: getId(context.resourceUrl),
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: context.name,
            access: 'read',
          },
          displayname: {
            value: context.displayName,
            access: 'read',
          },
          app: {
            value: context.appName,
            access: 'read',
          },
          namespace: {
            value: context.namespaceName,
            access: 'read',
          },
        },
      }));
    }
    case 'capability': {
      const split = id.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      function getId(url: string): string {
        const split = url.split('/');
        return `${split[split.length - 3]}:${split[split.length - 2]}:${split[split.length - 1]}`
      }
      const data: WrappedCapabilitiesList = await adapterStore.dataAdapter.fetchCapabilities(role, values.appSelection, values.namespaceSelection);
      return data.capabilities.map(capability => ({
        id: `${capability.appName}:${capability.namespaceName}:${capability.name}`,
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: capability.name,
            access: 'read',
          },
          displayname: {
            value: capability.displayName,
            access: 'read',
          },
          app: {
            value: capability.appName,
            access: 'read',
          },
          namespace: {
            value: capability.namespaceName,
            access: 'read',
          },
        },
      }));
    }
  }
  return [];
};

export const fetchObject = async (
  objectType: ObjectType,
  id: string
): Promise<DetailResponseModel | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  console.log('fetch: ', id);
  switch (objectType) {
    case 'role': {
      const split = id.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedRole = await adapterStore.dataAdapter.fetchRole(role.appName, role.namespaceName, role.name);
      const config = JSON.parse(JSON.stringify(roleDetailResponseModel));
      config.values = data.role;
      delete config.values.resourceUrl;
      return config;
    }
    case 'namespace': {
      const split = id.split(':');
      const namespace = {
        appName: split[0],
        name: split[1],
      };
      const data: WrappedNamespace = await adapterStore.dataAdapter.fetchNamespace(namespace.appName, namespace.name);
      const config = JSON.parse(JSON.stringify(namespaceDetailResponseModel));
      config.values = data.namespace;
      delete config.values.resourceUrl;
      return config;
    }
    case 'context': {
      const split = id.split(':');
      const context = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedContext = await adapterStore.dataAdapter.fetchContext(context.appName, context.namespaceName, context.name);
      const config = JSON.parse(JSON.stringify(contextDetailResponseModel));
      config.values = data.context;
      delete config.values.resourceUrl;
      return config;
    }
    case 'capability': {
      const split = id.split(':');
      const capability = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      console.log('cap: ', capability);
      const data: WrappedCapability = await adapterStore.dataAdapter.fetchCapability(capability.appName, capability.namespaceName, capability.name);
      console.log('data: ', data);
      const config = JSON.parse(JSON.stringify(capabilityDetailResponseModel));
      config.values = data.capability;
      config.values.permissions = [];
      delete config.values.resourceUrl;
      console.log('config: ', config);
      return config;
    }
  }
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
  objectType: ObjectType,
  values: FormValues
): Promise<SaveError | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      const data: WrappedRole = await adapterStore.dataAdapter.updateRole(values);
      return null;
    }
    case 'namespace': {
      const data: WrappedNamespace = await adapterStore.dataAdapter.updateNamespace(values);
      return null;
    }
    case 'context': {
      const data: WrappedContext = await adapterStore.dataAdapter.updateContext(values);
      return null;
    }
  }
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
  values: FormValues
): Promise<CreateObjectResponse> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      const data: WrappedRole = await adapterStore.dataAdapter.createRole(values);
      return {
        status: 'success',
        name: data.role.name,
      };
    }
    case 'namespace': {
      const data: WrappedNamespace = await adapterStore.dataAdapter.createNamespace(values);
      return {
        status: 'success',
        name: data.namespace.name,
      };
    }
    case 'context': {
      const data: WrappedContext = await adapterStore.dataAdapter.createContext(values);
      return {
        status: 'success',
        name: data.context.name,
      };
    }
    case 'capability': {
      console.log('create capability: ', values);
    }
  }
};

export const deleteCapabilities = async (ids: string[]): Promise<{id: string; error: string}[]> => {
  if (needMock) {
    return fetchMockData(
      [
        {
          id: ids[0] as string,
          error: 'some error',
        },
      ],
      'deleteCapabilities'
    );
  }

  console.log('Real backend call not implemented yet. Returning mock data');
  return fetchMockData(
    [
      {
        id: ids[0] as string,
        error: 'some error',
      },
    ],
    'deleteCapabilities'
  );

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


export const fetchNamespacesOptions = async (appName: string, withAllOption: boolean): Promise<LabeledValue<string>[]> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const namespaces: WrappedNamespacesList = await adapterStore.dataAdapter.fetchNamespaces(appName);
  const namespacesOptions = namespaces.namespaces.map(namespace => ({
    value: namespace.name,
    label: namespace.displayName || namespace.name,
  }));
  if (withAllOption) {
    namespacesOptions.unshift({
      label: 'All',
      value: '',
    });
  }

  return namespacesOptions;
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
export const fetchPermissionsOptions = async (appName: string, namespaceName: string): Promise<LabeledValue<string>[]> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const permissions: WrappedPermissionsList = await adapterStore.dataAdapter.fetchPermissions(appName, namespaceName);
  const permissionsOptions = permissions.permissions.map(permission => ({
    value: permission.name,
    label: permission.displayName || permission.name,
  }));

  return permissionsOptions;
};
