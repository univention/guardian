import i18next from 'i18next';
import {v4 as uuid4} from 'uuid';
import type {AuthenticationPort} from '@/ports/authentication';
import type {DataPort} from '@/ports/data';
import type {AppResponseData, AppsResponse, DisplayApp, WrappedAppsList} from '@/helpers/models/apps';
import type {
  DisplayNamespace,
  Namespace,
  NamespaceRequestData,
  NamespaceResponse,
  NamespaceResponseData,
  NamespacesResponse,
  WrappedNamespace,
  WrappedNamespacesList,
} from '@/helpers/models/namespaces';
import type {
  DisplayRole,
  Role,
  RoleRequestData,
  RoleResponse,
  RoleResponseData,
  RolesResponse,
  WrappedRole,
  WrappedRolesList,
} from '@/helpers/models/roles';
import type {
  Context,
  ContextRequestData,
  ContextResponse,
  ContextResponseData,
  ContextsResponse,
  DisplayContext,
  WrappedContext,
  WrappedContextsList,
} from '@/helpers/models/contexts';
import type {
  CapabilitiesResponse,
  Capability,
  CapabilityCondition,
  CapabilityConditionRequestData,
  CapabilityParameter,
  CapabilityParameterRequestData,
  CapabilityPermission,
  CapabilityPermissionRequestData,
  CapabilityRequestData,
  CapabilityResponse,
  CapabilityResponseData,
  CapabilityRole,
  CapabilityRoleRequestData,
  DisplayCapability,
  NewCapability,
  NewCapabilityRequestData,
  WrappedCapabilitiesList,
  WrappedCapability,
} from '@/helpers/models/capabilities';
import type {
  DisplayPermission,
  PermissionResponseData,
  PermissionsResponse,
  WrappedPermissionsList,
} from '@/helpers/models/permissions';
import type {
  ConditionParameter,
  ConditionResponseData,
  ConditionsResponse,
  DisplayCondition,
  WrappedConditionsList,
} from '@/helpers/models/conditions';
import {makeMockApps, makeMockAppsResponse} from '@/helpers/mocks/api/apps';
import {makeMockNamespaces, makeMockNamespacesResponse} from '@/helpers/mocks/api/namespaces';
import {makeMockRoles, makeMockRolesResponse} from '@/helpers/mocks/api/roles';
import {makeMockContexts, makeMockContextsResponse} from '@/helpers/mocks/api/contexts';
import {makeMockPermissions, makeMockPermissionsResponse} from '@/helpers/mocks/api/permissions';
import {makeMockConditions, makeMockConditionsResponse} from '@/helpers/mocks/api/conditions';
import {makeMockCapabilities, makeMockCapabilitiesResponse} from '@/helpers/mocks/api/capabilities';

export type Result<T, E> =
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      error: E;
    };

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
    } catch (_err) {
      // Either not a JSON response, or unparsable. We'll just ignore this.
    }
    return detail;
  }
  return null;
};
const getErrorString = (error: {detail: unknown}): string => {
  if (error.detail !== null && typeof error.detail === 'object' && 'message' in error.detail) {
    return JSON.stringify(error.detail.message);
  } else {
    // technically could fail
    return JSON.stringify(error.detail);
  }
};

export type SaveError =
  | {
      type: 'objectNotFound';
    }
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
const getSaveError = async (response: Response): Promise<SaveError | null> => {
  const errorJson = await getError(response);
  if (!errorJson) {
    return null;
  }
  if (response.status === 422) {
    // FIXME validate format of errorJson
    // We assume here that errorJson.detail has a specific format when we get a 422 status.
    // We should validate that that is true.
    //
    // It would be nice to have a shared json.schema between frontend and backend to facilitate
    // good/stable/exhaustive/type checked error handling.
    //
    // Ideally the json.schema would describe a set of tagged unions for all possible backend errors.
    // Although that might collide/overlap with the status codes a bit.
    //
    // e.g.
    // {
    //   type: 'validationError',
    //   detail: ...
    // }
    //
    // {
    //   type: 'nameTakenError'
    // }

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
  if (
    errorJson.detail !== null &&
    typeof errorJson.detail === 'object' &&
    'message' in errorJson.detail &&
    errorJson.detail.message === 'An object with the given identifiers already exists.' // FIXME: It would be nice to get a more explicit error type for this from the backend
  ) {
    return {
      type: 'fieldErrors',
      errors: [
        {
          field: 'name',
          message: i18next.t('dataAdapter.create.nameTaken'),
        },
      ],
    };
  }
  if (response.status === 404) {
    return {
      type: 'objectNotFound',
    };
  }
  return {
    type: 'generic',
    message: getErrorString(errorJson),
  };
};

export type FetchObjectError =
  | {
      type: 'objectNotFound';
    }
  | {
      type: 'generic';
      message: string;
    };

export const apiDataSettings = {
  uri: 'apiDataAdapter.uri',
  useProxy: 'managementUi.cors.useProxy',
};

class GenericDataAdapter implements DataPort {
  async fetchApps(): Promise<Result<WrappedAppsList, string>> {
    const result = await this.fetchAppsRequest();
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        apps: result.value.apps.map(app => this._appFromApi(app)),
      },
    };
  }

  async fetchNamespaces(app?: string): Promise<Result<WrappedNamespacesList, string>> {
    const result = await this.fetchNamespacesRequest(app);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        namespaces: result.value.namespaces.map(namespace => this._namespaceFromApi(namespace)),
      },
    };
  }

  async fetchNamespace(app: string, name: string): Promise<Result<WrappedNamespace, FetchObjectError>> {
    const result = await this.fetchNamespaceRequest(app, name);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        namespace: this._namespaceFromApi(result.value.namespace),
      },
    };
  }

  async createNamespace(namespace: Namespace): Promise<Result<WrappedNamespace, SaveError>> {
    const requestData = this._namespaceToApi(namespace);
    const result = await this.createNamespaceRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        namespace: this._namespaceFromApi(result.value.namespace),
      },
    };
  }

  async updateNamespace(namespace: Namespace): Promise<Result<WrappedNamespace, SaveError>> {
    const requestData = this._namespaceToApi(namespace);
    const result = await this.updateNamespaceRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        namespace: this._namespaceFromApi(result.value.namespace),
      },
    };
  }

  async fetchRoles(app?: string, namespace?: string): Promise<Result<WrappedRolesList, string>> {
    const result = await this.fetchRolesRequest(app, namespace);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        roles: result.value.roles.map(role => this._roleFromApi(role)),
      },
    };
  }

  async fetchRole(app: string, namespace: string, name: string): Promise<Result<WrappedRole, FetchObjectError>> {
    const result = await this.fetchRoleRequest(app, namespace, name);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        role: this._roleFromApi(result.value.role),
      },
    };
  }

  async createRole(role: Role): Promise<Result<WrappedRole, SaveError>> {
    const requestData = this._roleToApi(role);
    const result = await this.createRoleRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        role: this._roleFromApi(result.value.role),
      },
    };
  }

  async updateRole(role: Role): Promise<Result<WrappedRole, SaveError>> {
    const requestData = this._roleToApi(role);
    const result = await this.updateRoleRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        role: this._roleFromApi(result.value.role),
      },
    };
  }

  async fetchContexts(app?: string, namespace?: string): Promise<Result<WrappedContextsList, string>> {
    const result = await this.fetchContextsRequest(app, namespace);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        contexts: result.value.contexts.map(context => this._contextFromApi(context)),
      },
    };
  }

  async fetchContext(app: string, namespace: string, name: string): Promise<Result<WrappedContext, FetchObjectError>> {
    const result = await this.fetchContextRequest(app, namespace, name);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        context: this._contextFromApi(result.value.context),
      },
    };
  }

  async createContext(context: Context): Promise<Result<WrappedContext, SaveError>> {
    const requestData = this._contextToApi(context);
    const result = await this.createContextRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        context: this._contextFromApi(result.value.context),
      },
    };
  }

  async updateContext(context: Context): Promise<Result<WrappedContext, SaveError>> {
    const requestData = this._contextToApi(context);
    const result = await this.updateContextRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        context: this._contextFromApi(result.value.context),
      },
    };
  }

  async fetchCapabilities(
    role: CapabilityRole,
    app?: string,
    namespace?: string
  ): Promise<Result<WrappedCapabilitiesList, string>> {
    const roleData = this._capabilityRoleToApi(role);
    const result = await this.fetchCapabilitiesRequest(roleData);
    if (!result.ok) {
      return result;
    }
    const unfilteredResponseData = result.value;
    let responseData = unfilteredResponseData.capabilities;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        responseData = unfilteredResponseData.capabilities.filter(
          capability => capability.app_name === app && capability.namespace_name == namespace
        );
      } else {
        responseData = unfilteredResponseData.capabilities.filter(capability => capability.app_name === app);
      }
    }
    return {
      ok: true,
      value: {
        capabilities: responseData.map(capability => this._capabilityFromApi(capability)),
      },
    };
  }

  async fetchCapability(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<WrappedCapability, FetchObjectError>> {
    const result = await this.fetchCapabilityRequest(app, namespace, name);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        capability: this._capabilityFromApi(result.value.capability),
      },
    };
  }

  async createCapability(capability: NewCapability): Promise<Result<WrappedCapability, SaveError>> {
    const requestData = this._newCapabilityToApi(capability);
    const result = await this.createCapabilityRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        capability: this._capabilityFromApi(result.value.capability),
      },
    };
  }

  async updateCapability(capability: Capability): Promise<Result<WrappedCapability, SaveError>> {
    const requestData = this._capabilityToApi(capability);
    const result = await this.updateCapabilityRequest(requestData);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        capability: this._capabilityFromApi(result.value.capability),
      },
    };
  }

  async removeCapability(app: string, namespace: string, name: string): Promise<Result<null, string>> {
    return await this.removeCapabilityRequest(app, namespace, name);
  }

  async fetchPermissions(app: string, namespace: string): Promise<Result<WrappedPermissionsList, string>> {
    const result = await this.fetchPermissionsRequest(app, namespace);
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        permissions: result.value.permissions.map(permission => this._permissionFromApi(permission)),
      },
    };
  }

  async fetchConditions(): Promise<Result<WrappedConditionsList, string>> {
    const result = await this.fetchConditionsRequest();
    if (!result.ok) {
      return result;
    }
    return {
      ok: true,
      value: {
        conditions: result.value.conditions.map(condition => this._conditionFromApi(condition)),
      },
    };
  }

  _appFromApi(appData: AppResponseData): DisplayApp {
    return {
      name: appData.name,
      displayName: appData.display_name,
      resourceUrl: appData.resource_url,
    };
  }

  _namespaceFromApi(namespaceData: NamespaceResponseData): DisplayNamespace {
    return {
      appName: namespaceData.app_name,
      name: namespaceData.name,
      displayName: namespaceData.display_name,
      resourceUrl: namespaceData.resource_url,
    };
  }

  _namespaceToApi(namespace: Namespace): NamespaceRequestData {
    return {
      app_name: namespace.appName,
      name: namespace.name,
      display_name: namespace.displayName,
    };
  }

  _roleFromApi(roleData: RoleResponseData): DisplayRole {
    return {
      name: roleData.name,
      displayName: roleData.display_name,
      resourceUrl: roleData.resource_url,
      appName: roleData.app_name,
      namespaceName: roleData.namespace_name,
    };
  }

  _roleToApi(role: Role): RoleRequestData {
    return {
      app_name: role.appName,
      namespace_name: role.namespaceName,
      name: role.name,
      display_name: role.displayName,
    };
  }

  _contextFromApi(contextData: ContextResponseData): DisplayContext {
    return {
      name: contextData.name,
      displayName: contextData.display_name,
      resourceUrl: contextData.resource_url,
      appName: contextData.app_name,
      namespaceName: contextData.namespace_name,
    };
  }

  _contextToApi(context: Context): ContextRequestData {
    return {
      app_name: context.appName,
      namespace_name: context.namespaceName,
      name: context.name,
      display_name: context.displayName,
    };
  }

  _permissionFromApi(permissionData: PermissionResponseData): DisplayPermission {
    return {
      name: permissionData.name,
      displayName: permissionData.display_name,
      resourceUrl: permissionData.resource_url,
      appName: permissionData.app_name,
      namespaceName: permissionData.namespace_name,
    };
  }

  _conditionFromApi(conditionData: ConditionResponseData): DisplayCondition {
    const parameters: ConditionParameter[] = conditionData.parameters.map(param => {
      return {name: param.name};
    });

    return {
      name: conditionData.name,
      displayName: conditionData.display_name,
      resourceUrl: conditionData.resource_url,
      appName: conditionData.app_name,
      namespaceName: conditionData.namespace_name,
      documentation: conditionData.documentation,
      parameters: parameters,
    };
  }

  _capabilityFromApi(capabilityData: CapabilityResponseData): DisplayCapability {
    const role: CapabilityRole = {
      appName: capabilityData.role.app_name,
      namespaceName: capabilityData.role.namespace_name,
      name: capabilityData.role.name,
    };

    const conditions: CapabilityCondition[] = capabilityData.conditions.map(condition => {
      const parameters: CapabilityParameter[] = condition.parameters.map(param => {
        return {
          name: param.name,
          value: param.value,
        };
      });

      return {
        appName: condition.app_name,
        namespaceName: condition.namespace_name,
        name: condition.name,
        parameters: parameters,
      };
    });

    const permissions: CapabilityPermission[] = capabilityData.permissions.map(permission => {
      return {
        appName: permission.app_name,
        namespaceName: permission.namespace_name,
        name: permission.name,
      };
    });

    return {
      appName: capabilityData.app_name,
      namespaceName: capabilityData.namespace_name,
      name: capabilityData.name,
      displayName: capabilityData.display_name,
      role: role,
      conditions: conditions,
      relation: capabilityData.relation,
      permissions: permissions,
      resourceUrl: capabilityData.resource_url,
    };
  }

  _capabilityToApi(capability: Capability): CapabilityRequestData {
    const role: CapabilityRoleRequestData = {
      app_name: capability.role.appName,
      namespace_name: capability.role.namespaceName,
      name: capability.role.name,
    };

    const conditions: CapabilityConditionRequestData[] = capability.conditions.map(condition => {
      const parameters: CapabilityParameterRequestData[] = condition.parameters.map(param => {
        return {
          name: param.name,
          value: param.value,
        };
      });

      return {
        app_name: condition.appName,
        namespace_name: condition.namespaceName,
        name: condition.name,
        parameters: parameters,
      };
    });

    const permissions: CapabilityPermissionRequestData[] = capability.permissions.map(permission => {
      return {
        app_name: permission.appName,
        namespace_name: permission.namespaceName,
        name: permission.name,
      };
    });

    return {
      app_name: capability.appName,
      namespace_name: capability.namespaceName,
      name: capability.name,
      display_name: capability.displayName,
      role: role,
      conditions: conditions,
      relation: capability.relation,
      permissions: permissions,
    };
  }

  _newCapabilityToApi(capability: NewCapability): NewCapabilityRequestData {
    const role: CapabilityRoleRequestData = {
      app_name: capability.role.appName,
      namespace_name: capability.role.namespaceName,
      name: capability.role.name,
    };

    const conditions: CapabilityConditionRequestData[] = capability.conditions.map(condition => {
      const parameters: CapabilityParameterRequestData[] = condition.parameters.map(param => {
        return {
          name: param.name,
          value: param.value,
        };
      });

      return {
        app_name: condition.appName,
        namespace_name: condition.namespaceName,
        name: condition.name,
        parameters: parameters,
      };
    });

    const permissions: CapabilityPermissionRequestData[] = capability.permissions.map(permission => {
      return {
        app_name: permission.appName,
        namespace_name: permission.namespaceName,
        name: permission.name,
      };
    });

    const newCapability: NewCapabilityRequestData = {
      app_name: capability.appName,
      namespace_name: capability.namespaceName,
      display_name: capability.displayName,
      role: role,
      conditions: conditions,
      relation: capability.relation,
      permissions: permissions,
    };
    if (capability.name !== undefined && capability.name !== '') {
      newCapability.name = capability.name;
    }

    return newCapability;
  }

  _capabilityRoleToApi(role: CapabilityRole): CapabilityRoleRequestData {
    return {
      app_name: role.appName,
      namespace_name: role.namespaceName,
      name: role.name,
    };
  }

  fetchAppsRequest(): Promise<Result<AppsResponse, string>> {
    throw new Error('Not Implemented');
  }

  fetchNamespacesRequest(app?: string): Promise<Result<NamespacesResponse, string>> {
    throw new Error(`Not Implemented. app=${app}`);
  }

  fetchNamespaceRequest(app: string, name: string): Promise<Result<NamespaceResponse, FetchObjectError>> {
    throw new Error(`Not Implemented. app=${app}; name=${name}`);
  }

  createNamespaceRequest(namespaceData: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    throw new Error(`Not Implemented. namespace=${namespaceData}`);
  }

  updateNamespaceRequest(namespaceData: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    throw new Error(`Not Implemented. namespace=${namespaceData}`);
  }

  fetchRolesRequest(app?: string, namespace?: string): Promise<Result<RolesResponse, string>> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchRoleRequest(app: string, namespace: string, name: string): Promise<Result<RoleResponse, FetchObjectError>> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createRoleRequest(roleData: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  updateRoleRequest(roleData: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  fetchContextsRequest(app?: string, namespace?: string): Promise<Result<ContextsResponse, string>> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchContextRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<ContextResponse, FetchObjectError>> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createContextRequest(contextData: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    throw new Error(`Not Implemented. context=${contextData}`);
  }

  updateContextRequest(contextData: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    throw new Error(`Not Implemented. context=${contextData}`);
  }

  fetchPermissionsRequest(app: string, namespace: string): Promise<Result<PermissionsResponse, string>> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchConditionsRequest(): Promise<Result<ConditionsResponse, string>> {
    throw new Error('Not Implemented');
  }

  fetchCapabilitiesRequest(roleData: CapabilityRoleRequestData): Promise<Result<CapabilitiesResponse, string>> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  fetchCapabilityRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<CapabilityResponse, FetchObjectError>> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createCapabilityRequest(capabilityData: NewCapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    throw new Error(`Not Implemented. capability=${capabilityData}`);
  }

  updateCapabilityRequest(capabilityData: CapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    throw new Error(`Not Implemented. capability=${capabilityData}`);
  }

  removeCapabilityRequest(app: string, namespace: string, name: string): Promise<Result<null, string>> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }
}

interface InMemoryDB {
  apps: AppResponseData[];
  namespaces: NamespaceResponseData[];
  roles: RoleResponseData[];
  contexts: ContextResponseData[];
  permissions: PermissionResponseData[];
  conditions: ConditionResponseData[];
  capabilities: CapabilityResponseData[];
}
export class InMemoryDataAdapter extends GenericDataAdapter {
  private readonly _responseTimeout = 1000;

  private _db: InMemoryDB = {
    apps: [],
    namespaces: [],
    roles: [],
    contexts: [],
    permissions: [],
    conditions: [],
    capabilities: [],
  };

  constructor(dbData?: InMemoryDB) {
    super();
    if (dbData) {
      this._db = dbData;
    } else {
      this._db.apps = makeMockApps();
      this._db.namespaces = makeMockNamespaces();
      this._db.roles = makeMockRoles();
      this._db.contexts = makeMockContexts();
      this._db.permissions = makeMockPermissions();
      this._db.conditions = makeMockConditions();
      this._db.capabilities = makeMockCapabilities();
    }
  }

  fetchAppsRequest(): Promise<Result<AppsResponse, string>> {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockAppsResponse(this._db.apps),
        });
      }, this._responseTimeout);
    });
  }

  fetchNamespacesRequest(app?: string): Promise<Result<NamespacesResponse, string>> {
    let mockNamespaces = this._db.namespaces;
    if (app !== undefined && app !== '') {
      mockNamespaces = this._db.namespaces.filter(namespace => namespace.app_name === app);
    }
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockNamespacesResponse(mockNamespaces),
        });
      }, this._responseTimeout);
    });
  }

  fetchNamespaceRequest(app: string, name: string): Promise<Result<NamespaceResponse, FetchObjectError>> {
    const mockNamespace = this._db.namespaces.find(ns => ns.app_name === app && ns.name === name);
    if (!mockNamespace) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        });
      });
    }

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {
            namespace: mockNamespace,
          },
        });
      }, this._responseTimeout);
    });
  }

  createNamespaceRequest(namespaceData: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    const existingNamespace = this._db.namespaces.find(
      ns => ns.app_name === namespaceData.app_name && ns.name === namespaceData.name
    );
    if (existingNamespace) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'fieldErrors',
              errors: [
                {
                  field: 'name',
                  message: i18next.t('dataAdapter.create.nameTaken'),
                },
              ],
            },
          });
        }, this._responseTimeout);
      });
    }

    const newNamespace: NamespaceResponseData = {
      resource_url: `http://localhost/guardian/management/namespaceDatas/${namespaceData.app_name}/${namespaceData.name}`,
      ...namespaceData,
    };
    this._db.namespaces.push(newNamespace);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {namespace: newNamespace},
        });
      }, this._responseTimeout);
    });
  }

  updateNamespaceRequest(namespaceData: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    const existingNamespace = this._db.namespaces.find(
      ns => ns.app_name === namespaceData.app_name && ns.name === namespaceData.name
    );
    if (!existingNamespace) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    const updatedNamespace = existingNamespace;
    updatedNamespace.display_name = namespaceData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {namespace: updatedNamespace},
        });
      }, this._responseTimeout);
    });
  }

  fetchRolesRequest(app?: string, namespace?: string): Promise<Result<RolesResponse, string>> {
    let mockRoles = this._db.roles;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        mockRoles = this._db.roles.filter(role => role.app_name === app && role.namespace_name === namespace);
      } else {
        mockRoles = this._db.roles.filter(role => role.app_name === app);
      }
    }
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockRolesResponse(mockRoles),
        });
      }, this._responseTimeout);
    });
  }

  fetchRoleRequest(app: string, namespace: string, name: string): Promise<Result<RoleResponse, FetchObjectError>> {
    const mockRole = this._db.roles.find(
      role => role.app_name === app && role.namespace_name == namespace && role.name === name
    );
    if (!mockRole) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {role: mockRole},
        });
      }, this._responseTimeout);
    });
  }

  createRoleRequest(roleData: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    const existingRole = this._db.roles.find(
      rl =>
        rl.app_name === roleData.app_name && rl.namespace_name === roleData.namespace_name && rl.name === roleData.name
    );
    if (existingRole) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'fieldErrors',
              errors: [
                {
                  field: 'name',
                  message: i18next.t('dataAdapter.create.nameTaken'),
                },
              ],
            },
          });
        }, this._responseTimeout);
      });
    }

    const newRole: RoleResponseData = {
      resource_url: `http://localhost/guardian/management/roleDatas/${roleData.app_name}/${roleData.namespace_name}/${roleData.name}`,
      ...roleData,
    };
    this._db.roles.push(newRole);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {role: newRole},
        });
      }, this._responseTimeout);
    });
  }

  updateRoleRequest(roleData: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    const existingRole = this._db.roles.find(
      rl =>
        rl.app_name === roleData.app_name && rl.namespace_name === roleData.namespace_name && rl.name === roleData.name
    );
    if (!existingRole) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    const updatedRole = existingRole;
    updatedRole.display_name = roleData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {role: updatedRole},
        });
      }, this._responseTimeout);
    });
  }

  fetchContextsRequest(app?: string, namespace?: string): Promise<Result<ContextsResponse, string>> {
    let mockContexts = this._db.contexts;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        mockContexts = this._db.contexts.filter(
          context => context.app_name === app && context.namespace_name === namespace
        );
      } else {
        mockContexts = this._db.contexts.filter(context => context.app_name === app);
      }
    }
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockContextsResponse(mockContexts),
        });
      }, this._responseTimeout);
    });
  }

  fetchContextRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<ContextResponse, FetchObjectError>> {
    const mockContext = this._db.contexts.find(
      context => context.app_name === app && context.namespace_name == namespace && context.name === name
    );
    if (!mockContext) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {context: mockContext},
        });
      }, this._responseTimeout);
    });
  }

  createContextRequest(contextData: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    const existingContext = this._db.contexts.find(
      ctx =>
        ctx.app_name === contextData.app_name &&
        ctx.namespace_name === contextData.namespace_name &&
        ctx.name === contextData.name
    );
    if (existingContext) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'fieldErrors',
              errors: [
                {
                  field: 'name',
                  message: i18next.t('dataAdapter.create.nameTaken'),
                },
              ],
            },
          });
        }, this._responseTimeout);
      });
    }

    const newContext: ContextResponseData = {
      app_name: contextData.app_name,
      namespace_name: contextData.namespace_name,
      name: contextData.name,
      display_name: contextData.display_name,
      resource_url: `http://localhost/guardian/management/contexts/${contextData.app_name}/${contextData.namespace_name}/${contextData.name}`,
    };
    this._db.contexts.push(newContext);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {context: newContext},
        });
      }, this._responseTimeout);
    });
  }

  updateContextRequest(contextData: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    const existingContext = this._db.contexts.find(
      ctx =>
        ctx.app_name === contextData.app_name &&
        ctx.namespace_name === contextData.namespace_name &&
        ctx.name === contextData.name
    );
    if (!existingContext) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        });
      });
    }

    const updatedContext = existingContext;
    updatedContext.display_name = contextData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {context: updatedContext},
        });
      }, this._responseTimeout);
    });
  }

  fetchPermissionsRequest(app: string, namespace: string): Promise<Result<PermissionsResponse, string>> {
    const mockPermissions = this._db.permissions.filter(
      permission => permission.app_name === app && permission.namespace_name === namespace
    );
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockPermissionsResponse(mockPermissions),
        });
      }, this._responseTimeout);
    });
  }

  fetchConditionsRequest(): Promise<Result<ConditionsResponse, string>> {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockConditionsResponse(this._db.conditions),
        });
      }, this._responseTimeout);
    });
  }

  fetchCapabilitiesRequest(roleData: CapabilityRoleRequestData): Promise<Result<CapabilitiesResponse, string>> {
    const mockCapabilities = this._db.capabilities.filter(
      capability =>
        capability.role.app_name === roleData.app_name &&
        capability.role.namespace_name === roleData.namespace_name &&
        capability.role.name === roleData.name
    );

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: makeMockCapabilitiesResponse(mockCapabilities),
        });
      }, this._responseTimeout);
    });
  }

  fetchCapabilityRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<CapabilityResponse, FetchObjectError>> {
    const mockCapability = this._db.capabilities.find(
      capability => capability.app_name === app && capability.namespace_name == namespace && capability.name === name
    );
    if (!mockCapability) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {capability: mockCapability},
        });
      }, this._responseTimeout);
    });
  }

  createCapabilityRequest(capabilityData: NewCapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    const existingCapability = this._db.capabilities.find(
      cap =>
        cap.app_name === capabilityData.app_name &&
        cap.namespace_name === capabilityData.namespace_name &&
        cap.name === capabilityData.name
    );
    if (existingCapability) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'fieldErrors',
              errors: [
                {
                  field: 'name',
                  message: i18next.t('dataAdapter.create.nameTaken'),
                },
              ],
            },
          });
        }, this._responseTimeout);
      });
    }

    const newCapability: CapabilityResponseData = {
      app_name: capabilityData.app_name,
      namespace_name: capabilityData.namespace_name,
      name: capabilityData.name ?? uuid4(),
      display_name: capabilityData.display_name,
      role: capabilityData.role,
      relation: capabilityData.relation,
      conditions: capabilityData.conditions,
      permissions: capabilityData.permissions,
      resource_url: `http://localhost/guardian/management/capabilities/${capabilityData.app_name}/${capabilityData.namespace_name}/${name}`,
    };
    this._db.capabilities.push(newCapability);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {capability: newCapability},
        });
      }, this._responseTimeout);
    });
  }

  updateCapabilityRequest(capabilityData: CapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    const existingCapability = this._db.capabilities.find(
      cap =>
        cap.app_name === capabilityData.app_name &&
        cap.namespace_name === capabilityData.namespace_name &&
        cap.name === capabilityData.name
    );
    if (!existingCapability) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: false,
            error: {
              type: 'objectNotFound',
            },
          });
        }, this._responseTimeout);
      });
    }

    const updatedCapability = existingCapability;
    updatedCapability.display_name = capabilityData.display_name;
    updatedCapability.relation = capabilityData.relation;
    updatedCapability.conditions = capabilityData.conditions;
    updatedCapability.permissions = capabilityData.permissions;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: {capability: updatedCapability},
        });
      }, this._responseTimeout);
    });
  }

  removeCapabilityRequest(app: string, namespace: string, name: string): Promise<Result<null, string>> {
    const existingCapability = this._db.capabilities.find(
      cap => cap.app_name === app && cap.namespace_name === namespace && cap.name === name
    );

    // if (!existingCapability) {
    //   pass
    //   we treat deleting non existent objects as success
    // }

    if (existingCapability) {
      const index = this._db.capabilities.indexOf(existingCapability);
      this._db.capabilities.splice(index, 1);
    }

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          ok: true,
          value: null,
        });
      }, this._responseTimeout);
    });
  }
}

export class ApiDataAdapter extends GenericDataAdapter {
  private readonly _authAdapter: AuthenticationPort;
  private readonly _apiUri: string;
  // Proxy settings are for development use only.
  // Please see vite.config.ts for proxy setup.
  private _useProxy: boolean = false;

  constructor(authAdapter: AuthenticationPort, apiUri: string, useProxy: boolean = false) {
    super();
    this._authAdapter = authAdapter;

    // Remove a trailing slash, if one exists,
    // so we always create a correct URL.
    let url = apiUri.replace(/\/$/, '');
    if (useProxy) {
      const baseUrl = new URL(url);
      url = baseUrl.pathname;
    }
    this._apiUri = url;
    this._useProxy = useProxy;
  }

  async tryToJson<T>(response: Response): Promise<Result<T, string>> {
    const result = await this.tryFn(() => response.json());
    if (!result.ok) {
      return {
        ok: false,
        error: i18next.t('dataAdapter.jsonError', {msg: result.error}),
      };
    }
    // TODO: Add run-time checks that `result.value` is of type `T`
    // response.json() returns `any` as type so the type check against `T` will
    // always work but might actually be wrong.
    // Add run-time checks
    return result;
  }

  async _fetchList<T>(endpoint: string): Promise<Result<T, string>> {
    const result = await this._get(endpoint);
    if (!result.ok) {
      return result;
    }

    const error = await getError(result.value);
    if (error) {
      return {
        ok: false,
        error: getErrorString(error),
      };
    }
    return this.tryToJson<T>(result.value);
  }

  async fetchAppsRequest(): Promise<Result<AppsResponse, string>> {
    const endpoint = this._makeUrl('/apps');
    return this._fetchList<AppsResponse>(endpoint);
  }

  async fetchNamespacesRequest(app?: string): Promise<Result<NamespacesResponse, string>> {
    let endpoint = this._makeUrl('/namespaces');
    if (app !== undefined && app !== '') {
      endpoint = this._makeUrl(`/namespaces/${app}`);
    }
    return this._fetchList<NamespacesResponse>(endpoint);
  }

  async _fetchObject<T>(endpoint: string): Promise<Result<T, FetchObjectError>> {
    const result = await this._get(endpoint);
    if (!result.ok) {
      return {
        ok: false,
        error: {
          type: 'generic',
          message: result.error,
        },
      };
    }

    const error = await getError(result.value);
    if (error) {
      if (result.value.status === 404) {
        return {
          ok: false,
          error: {
            type: 'objectNotFound',
          },
        };
      }
      return {
        ok: false,
        error: {
          type: 'generic',
          message: getErrorString(error),
        },
      };
    }
    const jsonResult = await this.tryToJson<T>(result.value);
    if (!jsonResult.ok) {
      return {
        ok: false,
        error: {
          type: 'generic',
          message: jsonResult.error,
        },
      };
    }
    return jsonResult;
  }

  async fetchNamespaceRequest(app: string, name: string): Promise<Result<NamespaceResponse, FetchObjectError>> {
    const endpoint = this._makeUrl(`/namespaces/${app}/${name}`);
    return this._fetchObject<NamespaceResponse>(endpoint);
  }

  async _save<T>(endpoint: string, request: any, method: 'post' | 'put' | 'patch'): Promise<Result<T, SaveError>> {
    const _method = {
      post: this._post,
      put: this._put,
      patch: this._patch,
    }[method].bind(this);
    const result = await _method(endpoint, request);
    if (!result.ok) {
      return {
        ok: false,
        error: {
          type: 'generic',
          message: result.error,
        },
      };
    }

    const error = await getSaveError(result.value);
    if (error) {
      return {
        ok: false,
        error,
      };
    }

    const jsonResult = await this.tryToJson<T>(result.value);
    if (!jsonResult.ok) {
      return {
        ok: false,
        error: {
          type: 'generic',
          message: jsonResult.error,
        },
      };
    }
    return jsonResult;
  }

  async createNamespaceRequest(namespace: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    const endpoint = this._makeUrl(`/namespaces/${namespace.app_name}`);
    const request = {
      name: namespace.name,
      display_name: namespace.display_name,
    };
    return this._save<NamespaceResponse>(endpoint, request, 'post');
  }

  async updateNamespaceRequest(namespace: NamespaceRequestData): Promise<Result<NamespaceResponse, SaveError>> {
    const endpoint = this._makeUrl(`/namespaces/${namespace.app_name}/${namespace.name}`);
    const request = {display_name: namespace.display_name};
    return this._save<NamespaceResponse>(endpoint, request, 'patch');
  }

  async fetchRolesRequest(app?: string, namespace?: string): Promise<Result<RolesResponse, string>> {
    let endpoint = this._makeUrl(`/roles`);
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        endpoint = this._makeUrl(`/roles/${app}/${namespace}`);
      } else {
        endpoint = this._makeUrl(`/roles/${app}`);
      }
    }
    return this._fetchList<RolesResponse>(endpoint);
  }

  async fetchRoleRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<RoleResponse, FetchObjectError>> {
    const endpoint = this._makeUrl(`/roles/${app}/${namespace}/${name}`);
    return this._fetchObject<RoleResponse>(endpoint);
  }

  async createRoleRequest(role: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    const endpoint = this._makeUrl(`/roles/${role.app_name}/${role.namespace_name}`);
    const request = {
      name: role.name,
      display_name: role.display_name,
    };
    return this._save<RoleResponse>(endpoint, request, 'post');
  }

  async updateRoleRequest(role: RoleRequestData): Promise<Result<RoleResponse, SaveError>> {
    const endpoint = this._makeUrl(`/roles/${role.app_name}/${role.namespace_name}/${role.name}`);
    const request = {display_name: role.display_name};
    return this._save<RoleResponse>(endpoint, request, 'patch');
  }

  async fetchContextsRequest(app?: string, namespace?: string): Promise<Result<ContextsResponse, string>> {
    let endpoint = this._makeUrl('/contexts');
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        endpoint = this._makeUrl(`/contexts/${app}/${namespace}`);
      } else {
        endpoint = this._makeUrl(`/contexts/${app}`);
      }
    }
    return this._fetchList<ContextsResponse>(endpoint);
  }

  async fetchContextRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<ContextResponse, FetchObjectError>> {
    const endpoint = this._makeUrl(`/contexts/${app}/${namespace}/${name}`);
    return this._fetchObject<ContextResponse>(endpoint);
  }

  async createContextRequest(context: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    const endpoint = this._makeUrl(`/contexts/${context.app_name}/${context.namespace_name}`);
    const request = {
      name: context.name,
      display_name: context.display_name,
    };
    return this._save<ContextResponse>(endpoint, request, 'post');
  }

  async updateContextRequest(context: ContextRequestData): Promise<Result<ContextResponse, SaveError>> {
    const endpoint = this._makeUrl(`/contexts/${context.app_name}/${context.namespace_name}/${context.name}`);
    const request = {
      display_name: context.display_name,
    };
    return this._save<ContextResponse>(endpoint, request, 'patch');
  }

  async fetchCapabilitiesRequest(role: CapabilityRoleRequestData): Promise<Result<CapabilitiesResponse, string>> {
    const endpoint = this._makeUrl(`/roles/${role.app_name}/${role.namespace_name}/${role.name}/capabilities`);
    return this._fetchList<CapabilitiesResponse>(endpoint);
  }

  async fetchCapabilityRequest(
    app: string,
    namespace: string,
    name: string
  ): Promise<Result<CapabilityResponse, FetchObjectError>> {
    const endpoint = this._makeUrl(`/capabilities/${app}/${namespace}/${name}`);
    return this._fetchObject<CapabilityResponse>(endpoint);
  }

  async createCapabilityRequest(capability: NewCapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    const endpoint = this._makeUrl(`/capabilities/${capability.app_name}/${capability.namespace_name}`);
    const request: Record<string, any> = {
      display_name: capability.display_name,
      role: capability.role,
      conditions: capability.conditions,
      relation: capability.relation,
      permissions: capability.permissions,
    };
    if (capability.name !== undefined && capability.name !== '') {
      request.name = capability.name;
    }
    return this._save<CapabilityResponse>(endpoint, request, 'post');
  }

  async updateCapabilityRequest(capability: CapabilityRequestData): Promise<Result<CapabilityResponse, SaveError>> {
    const endpoint = this._makeUrl(
      `/capabilities/${capability.app_name}/${capability.namespace_name}/${capability.name}`
    );
    const request = {
      display_name: capability.display_name,
      role: capability.role,
      conditions: capability.conditions,
      relation: capability.relation,
      permissions: capability.permissions,
    };
    return this._save(endpoint, request, 'put');
  }

  async _deleteObject(endpoint: string): Promise<Result<null, string>> {
    const result = await this._delete(endpoint);
    if (!result.ok) {
      return result;
    }

    const error = await getError(result.value);
    if (error) {
      if (result.value.status === 404) {
        // we can treat already deleted objects as a success
        return {
          ok: true,
          value: null,
        };
      }
      return {
        ok: false,
        error: getErrorString(error),
      };
    } else {
      return {
        ok: true,
        value: null,
      };
    }
  }

  async removeCapabilityRequest(app: string, namespace: string, name: string): Promise<Result<null, string>> {
    const endpoint = this._makeUrl(`/capabilities/${app}/${namespace}/${name}`);
    return this._deleteObject(endpoint);
  }

  async fetchPermissionsRequest(app: string, namespace: string): Promise<Result<PermissionsResponse, string>> {
    const endpoint = this._makeUrl(`/permissions/${app}/${namespace}`);
    return this._fetchList(endpoint);
  }

  async fetchConditionsRequest(): Promise<Result<ConditionsResponse, string>> {
    const endpoint = this._makeUrl(`/conditions`);
    return this._fetchList(endpoint);
  }

  _makeUrl(endpoint: string): string {
    return `${this._apiUri}${endpoint}`;
  }

  async _makeHeaders(): Promise<HeadersInit> {
    const authHeader = await this._authAdapter.getValidAuthorizationHeader();
    const defaultHeaders = {
      'Accept-Language': i18next.language,
      accept: 'application/json',
      'Content-Type': 'application/json;charset=UTF-8',
    };
    return {
      ...defaultHeaders,
      ...authHeader,
    };
  }

  async tryFn<T>(fn: () => Promise<T>): Promise<Result<T, string>> {
    try {
      const value = await fn();
      return {
        ok: true,
        value,
      };
    } catch (err: unknown) {
      let errorMessage = i18next.t('dataAdapter.unknownError');
      if (err instanceof Error) {
        errorMessage = err.toString();
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else {
        try {
          errorMessage = JSON.stringify(err);
        } catch (_err) {
          // ignore
        }
      }
      return {
        ok: false,
        error: errorMessage,
      };
    }
  }

  async _fetch(fn: () => Promise<Response>, i18nContext: string): Promise<Result<Response, string>> {
    const result = await this.tryFn(fn);
    if (!result.ok) {
      return {
        ok: false,
        error: i18next.t('dataAdapter.fetchFailed', {
          context: i18nContext,
          msg: result.error,
        }),
      };
    }
    return result;
  }

  async _get(url: string): Promise<Result<Response, string>> {
    const headers = await this._makeHeaders();
    return this._fetch(() => fetch(url, {method: 'GET', headers: headers}), 'get');
  }

  async _post(url: string, request: any): Promise<Result<Response, string>> {
    const headers = await this._makeHeaders();
    return this._fetch(() => fetch(url, {method: 'POST', headers: headers, body: JSON.stringify(request)}), 'post');
  }

  async _patch(url: string, request: any): Promise<Result<Response, string>> {
    const headers = await this._makeHeaders();
    return this._fetch(() => fetch(url, {method: 'PATCH', headers: headers, body: JSON.stringify(request)}), 'patch');
  }

  async _put(url: string, request: any): Promise<Result<Response, string>> {
    const headers = await this._makeHeaders();
    return this._fetch(() => fetch(url, {method: 'PUT', headers: headers, body: JSON.stringify(request)}), 'put');
  }

  async _delete(url: string): Promise<Result<Response, string>> {
    const headers = await this._makeHeaders();
    return this._fetch(() => fetch(url, {method: 'DELETE', headers: headers}), 'delete');
  }
}
