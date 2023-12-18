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
import type {Namespace, WrappedNamespace} from '@/helpers/models/namespaces';
import type {Role, WrappedRole} from '@/helpers/models/roles';
import type {Context, WrappedContext} from '@/helpers/models/contexts';
import type {Capability, WrappedCapability} from '@/helpers/models/capabilities';
import type {DataPort} from '@/ports/data';
import type {FetchObjectError, Result, SaveError} from '@/adapters/data';

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

const getDataAdapter = async (): Promise<DataPort> => {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);
  return adapterStore.dataAdapter;
};

const fetchAppsOptions = async (withAllOption: boolean): Promise<Result<LabeledValue<string>[], string>> => {
  const dataAdapter = await getDataAdapter();

  const result = await dataAdapter.fetchApps();
  if (!result.ok) {
    return result;
  }
  const appsOptions = result.value.apps.map(app => ({
    value: app.name,
    label: app.displayName || app.name,
  }));
  if (withAllOption) {
    appsOptions.unshift({
      label: i18next.t('dataAccess.options.all'),
      value: '',
    });
  }

  return {
    ok: true,
    value: appsOptions,
  };
};
const fetchConditionSubElement = async (): Promise<Result<Field, string>> => {
  const dataAdapter = await getDataAdapter();

  const result = await dataAdapter.fetchConditions();
  if (!result.ok) {
    return result;
  }

  const extensions: Record<string, Field[]> = {};
  const options: {
    label: string;
    value: string;
  }[] = [];

  result.value.conditions.forEach(condition => {
    const conditionId = `${condition.appName}:${condition.namespaceName}:${condition.name}`;

    if (condition.parameters.length > 0) {
      const inputs: {type: any; props: any}[] = [];
      condition.parameters.forEach(param => {
        inputs.push({
          type: 'UInputText',
          props: {
            label: `${param.name}`,
            name: `${param.name}`,
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
    ok: true,
    value: {
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
    },
  };
};

export const fetchListViewConfig = async (): Promise<Result<ListViewConfigs, string>> => {
  const result = await fetchAppsOptions(true);
  if (!result.ok) {
    return result;
  }
  return {
    ok: true,
    value: getListViewConfig(result.value),
  };
};

export const fetchAddViewConfig = async (objectType: ObjectType): Promise<Result<AddViewConfig, string>> => {
  const result = await fetchAppsOptions(false);
  if (!result.ok) {
    return result;
  }

  const appsOptions = result.value;
  switch (objectType) {
    case 'role':
      return {
        ok: true,
        value: getAddRoleViewConfig(appsOptions),
      };
    case 'namespace':
      return {
        ok: true,
        value: getAddNamespaceViewConfig(appsOptions),
      };
    case 'context':
      return {
        ok: true,
        value: getAddContextViewConfig(appsOptions),
      };
    case 'capability': {
      const conditionsElement = await fetchConditionSubElement();
      if (!conditionsElement.ok) {
        return conditionsElement;
      }
      return {
        ok: true,
        value: getAddCapabilityViewConfig(appsOptions, conditionsElement.value),
      };
    }
  }
};

export const fetchObjects = async (
  objectType: ObjectType,
  values: FormValues,
  roleId: string
): Promise<Result<ListResponseModel[], string>> => {
  const dataAdapter = await getDataAdapter();

  switch (objectType) {
    case 'role': {
      const result = await dataAdapter.fetchRoles(values.appSelection as string, values.namespaceSelection as string);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.roles.map(role => ({
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
        })),
      };
    }
    case 'namespace': {
      const result = await dataAdapter.fetchNamespaces(values.appSelection as string);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.namespaces.map(namespace => ({
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
        })),
      };
    }
    case 'context': {
      const result = await dataAdapter.fetchContexts(
        values.appSelection as string,
        values.namespaceSelection as string
      );
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.contexts.map(ctx => ({
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
        })),
      };
    }
    case 'capability': {
      const split = roleId.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const result = await dataAdapter.fetchCapabilities(
        role,
        values.appSelection as string,
        values.namespaceSelection as string
      );
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.capabilities.map(capability => ({
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
        })),
      };
    }
  }
};

export const fetchObject = async (
  objectType: ObjectType,
  id: string
): Promise<Result<DetailResponseModel, FetchObjectError>> => {
  const dataAdapter = await getDataAdapter();

  switch (objectType) {
    case 'role': {
      const split = id.split(':');
      const role = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const result = await dataAdapter.fetchRole(role.appName, role.namespaceName, role.name);
      if (!result.ok) {
        return result;
      }
      const data = result.value;
      return {
        ok: true,
        value: getRoleDetailResponseModel({
          name: data.role.name,
          appName: data.role.appName,
          displayName: data.role.displayName,
          namespaceName: data.role.namespaceName,
        }),
      };
    }
    case 'namespace': {
      const split = id.split(':');
      const namespace = {
        appName: split[0],
        name: split[1],
      };
      const result = await dataAdapter.fetchNamespace(namespace.appName, namespace.name);
      if (!result.ok) {
        return result;
      }

      const data = result.value;
      return {
        ok: true,
        value: getNamespaceDetailResponseModel({
          name: data.namespace.name,
          appName: data.namespace.appName,
          displayName: data.namespace.displayName,
        }),
      };
    }
    case 'context': {
      const split = id.split(':');
      const context = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const result = await dataAdapter.fetchContext(context.appName, context.namespaceName, context.name);
      if (!result.ok) {
        return result;
      }
      const data = result.value;
      return {
        ok: true,
        value: getContextDetailResponseModel({
          name: data.context.name,
          appName: data.context.appName,
          namespaceName: data.context.namespaceName,
          displayName: data.context.displayName,
        }),
      };
    }
    case 'capability': {
      const split = id.split(':');
      const capability = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      const result = await dataAdapter.fetchCapability(capability.appName, capability.namespaceName, capability.name);
      if (!result.ok) {
        return result;
      }
      const data = result.value;
      const permissionsOptions = await fetchPermissionsOptions(data.capability.appName, data.capability.namespaceName);
      if (!permissionsOptions.ok) {
        return {
          ok: false,
          error: {
            type: 'generic',
            message: permissionsOptions.error,
          },
        };
      }
      const conditionsElement = await fetchConditionSubElement();
      if (!conditionsElement.ok) {
        return {
          ok: false,
          error: {
            type: 'generic',
            message: conditionsElement.error,
          },
        };
      }
      return {
        ok: true,
        value: getCapabilityDetailResponseModel(
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
          conditionsElement.value,
          permissionsOptions.value
        ),
      };
    }
  }
};

export const updateObject = async (
  objectType: ObjectType,
  values: FormValues,
  roleId: string,
  conditionsExtensions: null | Record<string, Field[]>
): Promise<Result<WrappedNamespace | WrappedRole | WrappedContext | WrappedCapability, SaveError>> => {
  const dataAdapter = await getDataAdapter();

  switch (objectType) {
    case 'role': {
      return await dataAdapter.updateRole(values as unknown as Role);
    }
    case 'namespace': {
      return await dataAdapter.updateNamespace(values as unknown as Namespace);
    }
    case 'context': {
      return await dataAdapter.updateContext(values as unknown as Context);
    }
    case 'capability': {
      if (conditionsExtensions === null) {
        return {
          ok: false,
          error: {
            type: 'generic',
            message: i18next.t('dataAccess.conditionsExtensionsEmptyError'),
          },
        };
      }
      const capability = getCapabilityFromFormValues(values, roleId, conditionsExtensions);
      return await dataAdapter.updateCapability(capability);
    }
  }
};

export const createObject = async (
  objectType: ObjectType,
  values: FormValues,
  roleId: string,
  conditionsExtensions: null | Record<string, Field[]>
): Promise<Result<string, SaveError>> => {
  const dataAdapter = await getDataAdapter();

  switch (objectType) {
    case 'role': {
      const result = await dataAdapter.createRole(values as unknown as Role);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.role.name,
      };
    }
    case 'namespace': {
      const result = await dataAdapter.createNamespace(values as unknown as Namespace);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.namespace.name,
      };
    }
    case 'context': {
      const result = await dataAdapter.createContext(values as unknown as Context);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.context.name,
      };
    }
    case 'capability': {
      if (conditionsExtensions === null) {
        return {
          ok: false,
          error: {
            type: 'generic',
            message: i18next.t('dataAccess.conditionsExtensionsEmptyError'),
          },
        };
      }
      const newCapability = getCapabilityFromFormValues(values, roleId, conditionsExtensions);
      const result = await dataAdapter.createCapability(newCapability);
      if (!result.ok) {
        return result;
      }
      return {
        ok: true,
        value: result.value.capability.name,
      };
    }
  }
};

export const deleteCapabilities = async (ids: string[]): Promise<{id: string; error: string}[]> => {
  const dataAdapter = await getDataAdapter();

  const data = await Promise.all(
    ids.map(id => {
      const split = id.split(':');
      const capability = {
        appName: split[0],
        namespaceName: split[1],
        name: split[2],
      };
      return dataAdapter.removeCapability(capability.appName, capability.namespaceName, capability.name);
    })
  );
  const errors = data.map(result => (result.ok ? null : result.error));
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
): Promise<Result<LabeledValue<string>[], string>> => {
  const dataAdapter = await getDataAdapter();

  const result = await dataAdapter.fetchNamespaces(appName);
  if (!result.ok) {
    return result;
  }
  const namespacesOptions = result.value.namespaces.map(namespace => ({
    value: namespace.name,
    label: namespace.displayName || namespace.name,
  }));
  if (withAllOption) {
    namespacesOptions.unshift({
      label: i18next.t('dataAccess.options.all'),
      value: '',
    });
  }

  return {
    ok: true,
    value: namespacesOptions,
  };
};

export const fetchPermissionsOptions = async (
  appName: string,
  namespaceName: string
): Promise<Result<LabeledValue<string>[], string>> => {
  const dataAdapter = await getDataAdapter();

  const result = await dataAdapter.fetchPermissions(appName, namespaceName);
  if (!result.ok) {
    return result;
  }
  const permissionsOptions = result.value.permissions.map(permission => ({
    value: permission.name,
    label: permission.displayName || permission.name,
  }));

  return {
    ok: true,
    value: permissionsOptions,
  };
};
