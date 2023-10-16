import type {
  AddViewConfig,
  DetailResponseModel,
  Field,
  FormValues,
  LabeledValue,
  ListResponseModel,
  ListViewConfigs,
  ObjectType,
} from '@/helpers/models';
import i18next from 'i18next';
import {
  getCapabilityDetailResponseModel,
  getContextDetailResponseModel,
  getRoleDetailResponseModel,
  getNamespaceDetailResponseModel,
  getListViewConfig,
  getAddRoleViewConfig,
  getAddContextViewConfig,
  getAddNamespaceViewConfig,
  getAddCapabilityViewConfig,
} from '@/helpers/configs';
import {useSettingsStore} from '@/stores/settings';
import {useAdapterStore} from '@/stores/adapter';
import type {WrappedAppsList} from '@/helpers/models/apps';
import type {Namespace, WrappedNamespacesList} from '@/helpers/models/namespaces';
import type {Role, WrappedRolesList} from '@/helpers/models/roles';
import type {Context, WrappedContextsList} from '@/helpers/models/contexts';
import type {Capability, WrappedCapabilitiesList} from '@/helpers/models/capabilities';
import type {WrappedRole} from '@/helpers/models/roles';
import type {WrappedNamespace} from '@/helpers/models/namespaces';
import type {WrappedContext} from '@/helpers/models/contexts';
import type {WrappedCapability} from '@/helpers/models/capabilities';
import type {WrappedPermissionsList} from '@/helpers/models/permissions';
import type {WrappedConditionsList} from '@/helpers/models/conditions';

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

const getCapabilityFromFormValues = (
  values: FormValues,
  roleId: string,
  conditionsExtensions: Record<string, Field[]>
): Capability => {
  const roleIdSplit = roleId.split(':');
  return {
    appName: values.appName as string,
    namespaceName: values.namespaceName as string,
    name: values.name as string,
    displayName: values.displayName as string,
    role: {
      appName: roleIdSplit[0],
      namespaceName: roleIdSplit[1],
      name: roleIdSplit[2],
    },
    conditions: (values.conditions as string[][]).map(condition => {
      const conditionName = condition[0];
      const conditionNameSplit = conditionName.split(':');
      const params = conditionsExtensions[conditionName];
      return {
        appName: conditionNameSplit[0],
        namespaceName: conditionNameSplit[1],
        name: conditionNameSplit[2],
        parameters: condition.slice(1).map((val, idx) => ({
          name: params[idx].props.name,
          value: val,
        })),
      };
    }),
    relation: values.relation as 'AND' | 'OR',
    permissions: (values.permissions as string[]).map(permission => ({
      appName: values.appName as string,
      namespaceName: values.namespaceName as string,
      name: permission,
    })),
  };
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
      label: i18next.t('dataAccess.options.all'),
      value: '',
    });
  }

  return appsOptions;
};
const fetchConditionSubElement = async (): Promise<Field> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const conditions: WrappedConditionsList = await adapterStore.dataAdapter.fetchConditions();

  const extensions: Record<string, Field[]> = {};
  const options: {
    label: string;
    value: string;
  }[] = [];

  conditions.conditions.forEach(condition => {
    const conditionId = `${condition.appName}:${condition.namespaceName}:${condition.name}`;

    if (condition.parameters.length > 0) {
      const inputs: {type: any; props: any}[] = [];
      condition.parameters.forEach(param => {
        inputs.push({
          type: 'UInputText',
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

  return {
    type: 'UExtendingInput',
    props: {
      name: 'conditions',
      label: '',
      extensions,
      rootElement: {
        type: 'UComboBox',
        props: {
          name: 'condition',
          label: i18next.t('configs.addView.field.condition'),
          options: options,
        },
      },
    },
  };
};

export const fetchListViewConfig = async (): Promise<ListViewConfigs> => {
  const appsOptions = await fetchAppsOptions(true);
  return getListViewConfig(appsOptions);
};

export const fetchAddViewConfig = async (objectType: ObjectType): Promise<AddViewConfig> => {
  const appsOptions = await fetchAppsOptions(false);

  switch (objectType) {
    case 'role':
      return getAddRoleViewConfig(appsOptions);
    case 'namespace':
      return getAddNamespaceViewConfig(appsOptions);
    case 'context':
      return getAddContextViewConfig(appsOptions);
    case 'capability': {
      const conditionsElement = await fetchConditionSubElement();
      return getAddCapabilityViewConfig(appsOptions, conditionsElement);
    }
  }
};

export const fetchObjects = async (
  objectType: ObjectType,
  values: FormValues,
  roleId: string
): Promise<ListResponseModel[] | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      const data: WrappedRolesList = await adapterStore.dataAdapter.fetchRoles(
        values.appSelection as string,
        values.namespaceSelection as string
      );
      return data.roles.map(role => ({
        id: `${role.appName}:${role.namespaceName}:${role.name}`,
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: role.name,
            access: 'read',
          },
          displayName: {
            value: role.displayName,
            access: 'read',
          },
          appName: {
            value: role.appName,
            access: 'read',
          },
          namespaceName: {
            value: role.namespaceName,
            access: 'read',
          },
        },
      }));
    }
    case 'namespace': {
      const data: WrappedNamespacesList = await adapterStore.dataAdapter.fetchNamespaces(values.appSelection as string);
      return data.namespaces.map(namespace => ({
        id: `${namespace.appName}:${namespace.name}`,
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: namespace.name,
            access: 'read',
          },
          displayName: {
            value: namespace.displayName,
            access: 'read',
          },
          appName: {
            value: namespace.appName,
            access: 'read',
          },
        },
      }));
    }
    case 'context': {
      const data: WrappedContextsList = await adapterStore.dataAdapter.fetchContexts(
        values.appSelection as string,
        values.namespaceSelection as string
      );
      return data.contexts.map(ctx => ({
        id: `${ctx.appName}:${ctx.namespaceName}:${ctx.name}`,
        allowedActions: ['edit'],
        attributes: {
          name: {
            value: ctx.name,
            access: 'read',
          },
          displayName: {
            value: ctx.displayName,
            access: 'read',
          },
          appName: {
            value: ctx.appName,
            access: 'read',
          },
          namespaceName: {
            value: ctx.namespaceName,
            access: 'read',
          },
        },
      }));
    }
    case 'capability': {
      const split = roleId.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedCapabilitiesList = await adapterStore.dataAdapter.fetchCapabilities(
        role,
        values.appSelection as string,
        values.namespaceSelection as string
      );
      return data.capabilities.map(capability => ({
        id: `${capability.appName}:${capability.namespaceName}:${capability.name}`,
        allowedActions: ['edit', 'delete'],
        attributes: {
          name: {
            value: capability.name,
            access: 'read',
          },
          displayName: {
            value: capability.displayName,
            access: 'read',
          },
          appName: {
            value: capability.appName,
            access: 'read',
          },
          namespaceName: {
            value: capability.namespaceName,
            access: 'read',
          },
        },
      }));
    }
  }
};

export const fetchObject = async (objectType: ObjectType, id: string): Promise<DetailResponseModel | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      const split = id.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedRole = await adapterStore.dataAdapter.fetchRole(role.appName, role.namespaceName, role.name);
      return getRoleDetailResponseModel({
        name: data.role.name,
        appName: data.role.appName,
        displayName: data.role.displayName,
        namespaceName: data.role.namespaceName,
      });
    }
    case 'namespace': {
      const split = id.split(':');
      const namespace = {
        appName: split[0],
        name: split[1],
      };
      const data: WrappedNamespace = await adapterStore.dataAdapter.fetchNamespace(namespace.appName, namespace.name);
      return getNamespaceDetailResponseModel({
        name: data.namespace.name,
        appName: data.namespace.appName,
        displayName: data.namespace.displayName,
      });
    }
    case 'context': {
      const split = id.split(':');
      const context = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedContext = await adapterStore.dataAdapter.fetchContext(
        context.appName,
        context.namespaceName,
        context.name
      );
      return getContextDetailResponseModel({
        name: data.context.name,
        appName: data.context.appName,
        namespaceName: data.context.namespaceName,
        displayName: data.context.displayName,
      });
    }
    case 'capability': {
      const split = id.split(':');
      const capability = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const data: WrappedCapability = await adapterStore.dataAdapter.fetchCapability(
        capability.appName,
        capability.namespaceName,
        capability.name
      );
      const permissionsOptions = await fetchPermissionsOptions(data.capability.appName, data.capability.namespaceName);
      const conditionsElement = await fetchConditionSubElement();
      return getCapabilityDetailResponseModel(
        {
          appName: data.capability.appName,
          namespaceName: data.capability.namespaceName,
          name: data.capability.name,
          displayName: data.capability.displayName,
          conditions: data.capability.conditions.map(condition => {
            const value = [`${condition.appName}:${condition.namespaceName}:${condition.name}`];
            for (const param of condition.parameters) {
              value.push(param.value);
            }
            return value;
          }),
          relation: data.capability.relation,
          permissions: data.capability.permissions.map(permission => permission.name),
        },
        conditionsElement,
        permissionsOptions
      );
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
  values: FormValues,
  roleId: string,
  conditionsExtensions: null | Record<string, Field[]>
): Promise<SaveError | null> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      await adapterStore.dataAdapter.updateRole(values as unknown as Role);
      return null;
    }
    case 'namespace': {
      await adapterStore.dataAdapter.updateNamespace(values as unknown as Namespace);
      return null;
    }
    case 'context': {
      await adapterStore.dataAdapter.updateContext(values as unknown as Context);
      return null;
    }
    case 'capability': {
      if (conditionsExtensions === null) {
        throw new Error('Unexpected internal error: conditionsExtension should not be null');
      }
      const capability = getCapabilityFromFormValues(values, roleId, conditionsExtensions);
      await adapterStore.dataAdapter.updateCapability(capability);
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
  values: FormValues,
  roleId: string,
  conditionsExtensions: null | Record<string, Field[]>
): Promise<CreateObjectResponse> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  switch (objectType) {
    case 'role': {
      const data: WrappedRole = await adapterStore.dataAdapter.createRole(values as unknown as Role);
      return {
        status: 'success',
        name: data.role.name,
      };
    }
    case 'namespace': {
      const data: WrappedNamespace = await adapterStore.dataAdapter.createNamespace(values as unknown as Namespace);
      return {
        status: 'success',
        name: data.namespace.name,
      };
    }
    case 'context': {
      const data: WrappedContext = await adapterStore.dataAdapter.createContext(values as unknown as Context);
      return {
        status: 'success',
        name: data.context.name,
      };
    }
    case 'capability': {
      if (conditionsExtensions === null) {
        throw new Error('Unexpected internal error: conditionsExtension should not be null');
      }
      const newCapability = getCapabilityFromFormValues(values, roleId, conditionsExtensions);
      const data: WrappedCapability = await adapterStore.dataAdapter.createCapability(newCapability);
      return {
        status: 'success',
        name: data.capability.name,
      };
    }
  }
};

export const deleteCapabilities = async (ids: string[]): Promise<{id: string; error: string}[]> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);

  const data = await Promise.all(ids.map(id => {
    const split = id.split(':');
    const capability = {
      appName: split[0],
      namespaceName: split[1],
      name: split[2],
    };
    return adapterStore.dataAdapter.removeCapability(capability.appName, capability.namespaceName, capability.name);
  }));
  const errors = data.map(success => success ? null : 'Could not delete'); // FIXME use errors from `removeCapability`
  const fails: {id: string; error: string}[] = [];
  for (let x = 0; x < data.length; x++) {
    const error = errors[x];
    if (error) {
      fails.push({
        id: ids[x],
        error,
      });
    }
  }
  return fails;
};

export const fetchNamespacesOptions = async (
  appName: string,
  withAllOption: boolean
): Promise<LabeledValue<string>[]> => {
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

export const fetchPermissionsOptions = async (
  appName: string,
  namespaceName: string
): Promise<LabeledValue<string>[]> => {
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
