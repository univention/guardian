import {v4 as uuid4} from 'uuid';
import type {DataPort} from '@/ports/data';
import type {AppResponseData, AppsResponse, DisplayApp, WrappedAppsList} from '@/helpers/models/apps';
import type {
  DisplayNamespace,
  Namespace,
  NamespaceResponse,
  NamespacesResponse,
  NamespaceRequestData,
  NamespaceResponseData,
  WrappedNamespace,
  WrappedNamespacesList,
} from '@/helpers/models/namespaces';
import type {
  DisplayRole,
  Role,
  RoleRequestData,
  RoleResponseData,
  RoleResponse,
  RolesResponse,
  WrappedRole,
  WrappedRolesList,
} from '@/helpers/models/roles';
import type {
  DisplayContext,
  Context,
  ContextResponseData,
  ContextResponse,
  ContextsResponse,
  ContextRequestData,
  WrappedContext,
  WrappedContextsList,
} from '@/helpers/models/contexts';
import type {
  Capability,
  CapabilityCondition,
  CapabilityConditionRequestData,
  CapabilityParameter,
  CapabilityParameterRequestData,
  CapabilityPermission,
  CapabilityPermissionRequestData,
  CapabilityRequestData,
  CapabilityRole,
  CapabilityRoleRequestData,
  CapabilityResponse,
  CapabilitiesResponse,
  CapabilityResponseData,
  DisplayCapability,
  NewCapability,
  NewCapabilityRequestData,
  WrappedCapability,
  WrappedCapabilitiesList,
} from '@/helpers/models/capabilities';
import type {
  DisplayPermission,
  PermissionsResponse,
  PermissionResponseData,
  WrappedPermissionsList,
} from '@/helpers/models/permissions';
import type {
  ConditionParameter,
  ConditionsResponse,
  ConditionResponseData,
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

export const inMemoryDataSettings = {
  loadData: 'inMemoryDataAdapter.loadData',
};

class GenericDataAdapter implements DataPort {
  async fetchApps(): Promise<WrappedAppsList> {
    const responseData = await this.fetchAppsRequest();
    const apps: DisplayApp[] = [];
    responseData.apps.forEach((app: AppResponseData) => {
      apps.push(this._appFromApi(app));
    });
    return new Promise(resolve => {
      resolve({apps: apps});
    });
  }

  async fetchNamespaces(app?: string): Promise<WrappedNamespacesList> {
    const responseData = await this.fetchNamespacesRequest(app);
    const namespaces: DisplayNamespace[] = [];
    responseData.namespaces.forEach((namespace: NamespaceResponseData) => {
      namespaces.push(this._namespaceFromApi(namespace));
    });
    return new Promise(resolve => {
      resolve({namespaces: namespaces});
    });
  }

  async fetchNamespace(app: string, name: string): Promise<WrappedNamespace> {
    const responseData = await this.fetchNamespaceRequest(app, name);
    const namespace = this._namespaceFromApi(responseData.namespace);
    return new Promise(resolve => {
      resolve({namespace: namespace});
    });
  }

  async createNamespace(namespace: Namespace): Promise<WrappedNamespace> {
    const requestData = this._namespaceToApi(namespace);
    const responseData = await this.createNamespaceRequest(requestData);
    const newNamespace = this._namespaceFromApi(responseData.namespace);
    return new Promise(resolve => {
      resolve({namespace: newNamespace});
    });
  }

  async updateNamespace(namespace: Namespace): Promise<WrappedNamespace> {
    const requestData = this._namespaceToApi(namespace);
    const responseData = await this.updateNamespaceRequest(requestData);
    const updatedNamespace = this._namespaceFromApi(responseData.namespace);
    return new Promise(resolve => {
      resolve({namespace: updatedNamespace});
    });
  }

  async fetchRoles(app?: string, namespace?: string): Promise<WrappedRolesList> {
    const responseData = await this.fetchRolesRequest(app, namespace);
    const roles: DisplayRole[] = [];
    responseData.roles.forEach((role: RoleResponseData) => {
      roles.push(this._roleFromApi(role));
    });
    return new Promise(resolve => {
      resolve({roles: roles});
    });
  }

  async fetchRole(app: string, namespace: string, name: string): Promise<WrappedRole> {
    const responseData = await this.fetchRoleRequest(app, namespace, name);
    const role = this._roleFromApi(responseData.role);
    return new Promise(resolve => {
      resolve({role: role});
    });
  }

  async createRole(role: Role): Promise<WrappedRole> {
    const requestData = this._roleToApi(role);
    const responseData = await this.createRoleRequest(requestData);
    const newRole = this._roleFromApi(responseData.role);
    return new Promise(resolve => {
      resolve({role: newRole});
    });
  }

  async updateRole(role: Role): Promise<WrappedRole> {
    const requestData = this._roleToApi(role);
    const responseData = await this.updateRoleRequest(requestData);
    const newRole = this._roleFromApi(responseData.role);
    return new Promise(resolve => {
      resolve({role: newRole});
    });
  }

  async fetchContexts(app?: string, namespace?: string): Promise<WrappedContextsList> {
    const responseData = await this.fetchContextsRequest(app, namespace);
    const contexts: DisplayContext[] = [];
    responseData.contexts.forEach((context: ContextResponseData) => {
      contexts.push(this._contextFromApi(context));
    });
    return new Promise(resolve => {
      resolve({contexts: contexts});
    });
  }

  async fetchContext(app: string, namespace: string, name: string): Promise<WrappedContext> {
    const responseData = await this.fetchContextRequest(app, namespace, name);
    const context = this._contextFromApi(responseData.context);
    return new Promise(resolve => {
      resolve({context: context});
    });
  }

  async createContext(context: Context): Promise<WrappedContext> {
    const requestData = this._contextToApi(context);
    const responseData = await this.createContextRequest(requestData);
    const newContext = this._contextFromApi(responseData.context);
    return new Promise(resolve => {
      resolve({context: newContext});
    });
  }

  async updateContext(context: Context): Promise<WrappedContext> {
    const requestData = this._contextToApi(context);
    const responseData = await this.updateContextRequest(requestData);
    const newContext = this._contextFromApi(responseData.context);
    return new Promise(resolve => {
      resolve({context: newContext});
    });
  }

  async fetchCapabilities(role: CapabilityRole, app?: string, namespace?: string): Promise<WrappedCapabilitiesList> {
    const roleData = this._capabilityRoleToApi(role);
    const unfilteredResponseData = await this.fetchCapabilitiesRequest(roleData);
    let responseData = unfilteredResponseData.capabilities;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        responseData = unfilteredResponseData.capabilities.filter((capability: CapabilityResponseData) => {
          return capability.app_name === app && capability.namespace_name == namespace;
        });
      } else {
        responseData = unfilteredResponseData.capabilities.filter((capability: CapabilityResponseData) => {
          return capability.app_name === app;
        });
      }
    }

    const capabilities: DisplayCapability[] = [];
    responseData.forEach((capability: CapabilityResponseData) => {
      capabilities.push(this._capabilityFromApi(capability));
    });

    return new Promise(resolve => {
      resolve({capabilities: capabilities});
    });
  }

  async fetchCapability(app: string, namespace: string, name: string): Promise<WrappedCapability> {
    const responseData = await this.fetchCapabilityRequest(app, namespace, name);
    const capability: DisplayCapability = this._capabilityFromApi(responseData.capability);
    return new Promise(resolve => {
      resolve({capability: capability});
    });
  }

  async createCapability(capability: NewCapability): Promise<WrappedCapability> {
    const requestData = this._newCapabilityToApi(capability);
    const responseData = await this.createCapabilityRequest(requestData);
    const newCapability = this._capabilityFromApi(responseData.capability);
    return new Promise(resolve => {
      resolve({capability: newCapability});
    });
  }

  async updateCapability(capability: Capability): Promise<WrappedCapability> {
    const requestData = this._capabilityToApi(capability);
    const responseData = await this.updateCapabilityRequest(requestData);
    const newCapability = this._capabilityFromApi(responseData.capability);
    return new Promise(resolve => {
      resolve({capability: newCapability});
    });
  }

  async removeCapability(app: string, namespace: string, name: string): Promise<boolean> {
    await this.removeCapabilityRequest(app, namespace, name);
    return new Promise(resolve => {
      resolve(true);
    });
  }

  async fetchPermissions(app: string, namespace: string): Promise<WrappedPermissionsList> {
    const responseData = await this.fetchPermissionsRequest(app, namespace);
    const permissions: DisplayPermission[] = [];
    responseData.permissions.forEach((permission: PermissionResponseData) => {
      permissions.push(this._permissionFromApi(permission));
    });
    return new Promise(resolve => {
      resolve({permissions: permissions});
    });
  }

  async fetchConditions(): Promise<WrappedConditionsList> {
    const responseData = await this.fetchConditionsRequest();
    const conditions: DisplayCondition[] = [];
    responseData.conditions.forEach((condition: ConditionResponseData) => {
      conditions.push(this._conditionFromApi(condition));
    });
    return new Promise(resolve => {
      resolve({conditions: conditions});
    });
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
    const parameters: ConditionParameter[] = [];
    conditionData.parameters.forEach(param => {
      parameters.push({name: param.name});
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

    const conditions: CapabilityCondition[] = [];
    capabilityData.conditions.forEach(condition => {
      const parameters: CapabilityParameter[] = [];
      condition.parameters.forEach(param => {
        parameters.push({
          name: param.name,
          value: param.value,
        });
      });

      conditions.push({
        appName: condition.app_name,
        namespaceName: condition.namespace_name,
        name: condition.name,
        parameters: parameters,
      });
    });

    const permissions: CapabilityPermission[] = [];
    capabilityData.permissions.forEach(permission => {
      permissions.push({
        appName: permission.app_name,
        namespaceName: permission.namespace_name,
        name: permission.name,
      });
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

    const conditions: CapabilityConditionRequestData[] = [];
    capability.conditions.forEach(condition => {
      const parameters: CapabilityParameterRequestData[] = [];
      condition.parameters.forEach(param => {
        parameters.push({
          name: param.name,
          value: param.value,
        });
      });

      conditions.push({
        app_name: condition.appName,
        namespace_name: condition.namespaceName,
        name: condition.name,
        parameters: parameters,
      });
    });

    const permissions: CapabilityPermissionRequestData[] = [];
    capability.permissions.forEach(permission => {
      permissions.push({
        app_name: permission.appName,
        namespace_name: permission.namespaceName,
        name: permission.name,
      });
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

    const conditions: CapabilityConditionRequestData[] = [];
    capability.conditions.forEach(condition => {
      const parameters: CapabilityParameterRequestData[] = [];
      condition.parameters.forEach(param => {
        parameters.push({
          name: param.name,
          value: param.value,
        });
      });

      conditions.push({
        app_name: condition.appName,
        namespace_name: condition.namespaceName,
        name: condition.name,
        parameters: parameters,
      });
    });

    const permissions: CapabilityPermissionRequestData[] = [];
    capability.permissions.forEach(permission => {
      permissions.push({
        app_name: permission.appName,
        namespace_name: permission.namespaceName,
        name: permission.name,
      });
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

  fetchAppsRequest(): Promise<AppsResponse> {
    throw new Error('Not Implemented');
  }

  fetchNamespacesRequest(app?: string): Promise<NamespacesResponse> {
    throw new Error(`Not Implemented. app=${app}`);
  }

  fetchNamespaceRequest(app: string, name: string): Promise<NamespaceResponse> {
    throw new Error(`Not Implemented. app=${app}; name=${name}`);
  }

  createNamespaceRequest(namespaceData: NamespaceRequestData): Promise<NamespaceResponse> {
    throw new Error(`Not Implemented. namespace=${namespaceData}`);
  }

  updateNamespaceRequest(namespaceData: NamespaceRequestData): Promise<NamespaceResponse> {
    throw new Error(`Not Implemented. namespace=${namespaceData}`);
  }

  fetchRolesRequest(app?: string, namespace?: string): Promise<RolesResponse> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchRoleRequest(app: string, namespace: string, name: string): Promise<RoleResponse> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createRoleRequest(roleData: RoleRequestData): Promise<RoleResponse> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  updateRoleRequest(roleData: RoleRequestData): Promise<RoleResponse> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  fetchContextsRequest(app?: string, namespace?: string): Promise<ContextsResponse> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchContextRequest(app: string, namespace: string, name: string): Promise<ContextResponse> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createContextRequest(contextData: ContextRequestData): Promise<ContextResponse> {
    throw new Error(`Not Implemented. context=${contextData}`);
  }

  updateContextRequest(contextData: ContextRequestData): Promise<ContextResponse> {
    throw new Error(`Not Implemented. context=${contextData}`);
  }

  fetchPermissionsRequest(app: string, namespace: string): Promise<PermissionsResponse> {
    throw new Error(`Not Implemented. app=${app}, namespace=${namespace}`);
  }

  fetchConditionsRequest(): Promise<ConditionsResponse> {
    throw new Error('Not Implemented');
  }

  fetchCapabilitiesRequest(roleData: CapabilityRoleRequestData): Promise<CapabilitiesResponse> {
    throw new Error(`Not Implemented. role=${roleData}`);
  }

  fetchCapabilityRequest(app: string, namespace: string, name: string): Promise<CapabilityResponse> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }

  createCapabilityRequest(capabilityData: NewCapabilityRequestData): Promise<CapabilityResponse> {
    throw new Error(`Not Implemented. capability=${capabilityData}`);
  }

  updateCapabilityRequest(capabilityData: CapabilityRequestData): Promise<CapabilityResponse> {
    throw new Error(`Not Implemented. capability=${capabilityData}`);
  }

  removeCapabilityRequest(app: string, namespace: string, name: string): Promise<{}> {
    throw new Error(`Not Implemented. app=${app}; namespace=${namespace}; name=${name}`);
  }
}

export class InMemoryDataAdapter extends GenericDataAdapter {
  private readonly _responseTimeout = 1000;

  private _db: {
    apps: AppResponseData[];
    namespaces: NamespaceResponseData[];
    roles: RoleResponseData[];
    contexts: ContextResponseData[];
    permissions: PermissionResponseData[];
    conditions: ConditionResponseData[];
    capabilities: CapabilityResponseData[];
  } = {
    apps: [],
    namespaces: [],
    roles: [],
    contexts: [],
    permissions: [],
    conditions: [],
    capabilities: [],
  };

  constructor() {
    super();
    this._db.apps = makeMockApps();
    this._db.namespaces = makeMockNamespaces();
    this._db.roles = makeMockRoles();
    this._db.contexts = makeMockContexts();
    this._db.permissions = makeMockPermissions();
    this._db.conditions = makeMockConditions();
    this._db.capabilities = makeMockCapabilities();
  }

  fetchAppsRequest(): Promise<AppsResponse> {
    const mockAppsResponse: AppsResponse = makeMockAppsResponse(this._db.apps);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockAppsResponse);
      }, this._responseTimeout);
    });
  }

  fetchNamespacesRequest(app?: string): Promise<NamespacesResponse> {
    let mockNamespaces = this._db.namespaces;
    if (app !== undefined && app !== '') {
      mockNamespaces = this._db.namespaces.filter(namespace => {
        return namespace.app_name === app;
      });
    }

    const mockNamespacesResponse: NamespacesResponse = makeMockNamespacesResponse(mockNamespaces);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockNamespacesResponse);
      }, this._responseTimeout);
    });
  }

  fetchNamespaceRequest(app: string, name: string): Promise<NamespaceResponse> {
    const mockNamespace: NamespaceResponseData[] = this._db.namespaces.filter(ns => {
      return ns.app_name === app && ns.name === name;
    });
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({namespace: mockNamespace[0]});
      }, this._responseTimeout);
    });
  }

  createNamespaceRequest(namespaceData: NamespaceRequestData): Promise<NamespaceResponse> {
    const existingNamespace =
      this._db.namespaces.filter(ns => {
        return ns.app_name === namespaceData.app_name && ns.name === namespaceData.name;
      }).length !== 0;
    if (existingNamespace) {
      // TODO: guardian#128: better error handling
      throw new Error('Namespace already exists');
    }

    const newNamespace: NamespaceResponseData = {
      resource_url: `http://localhost/guardian/management/namespaceDatas/${namespaceData.app_name}/${namespaceData.name}`,
      ...namespaceData,
    };
    this._db.namespaces.push(newNamespace);

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({namespace: newNamespace});
      }, this._responseTimeout);
    });
  }

  updateNamespaceRequest(namespaceData: NamespaceRequestData): Promise<NamespaceResponse> {
    const existingNamespace = this._db.namespaces.filter(ns => {
      return ns.app_name === namespaceData.app_name && ns.name === namespaceData.name;
    });
    if (existingNamespace.length === 0) {
      // TODO: guardian#128: better error handling
      throw new Error('Namespace does not exist');
    }
    const updatedNamespace = existingNamespace[0];
    updatedNamespace.display_name = namespaceData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({namespace: updatedNamespace});
      }, this._responseTimeout);
    });
  }

  fetchRolesRequest(app?: string, namespace?: string): Promise<RolesResponse> {
    let mockRoles = this._db.roles;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        mockRoles = this._db.roles.filter(role => {
          return role.app_name === app && role.namespace_name === namespace;
        });
      } else {
        mockRoles = this._db.roles.filter(role => {
          return role.app_name === app;
        });
      }
    }

    const mockRolesResponse: RolesResponse = makeMockRolesResponse(mockRoles);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockRolesResponse);
      }, this._responseTimeout);
    });
  }

  fetchRoleRequest(app: string, namespace: string, name: string): Promise<RoleResponse> {
    const mockRole: RoleResponseData[] = this._db.roles.filter(role => {
      return role.app_name === app && role.namespace_name == namespace && role.name === name;
    });
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({role: mockRole[0]});
      }, this._responseTimeout);
    });
  }

  createRoleRequest(roleData: RoleRequestData): Promise<RoleResponse> {
    const existingRole =
      this._db.roles.filter(rl => {
        return (
          rl.app_name === roleData.app_name &&
          rl.namespace_name === roleData.namespace_name &&
          rl.name === roleData.name
        );
      }).length !== 0;
    if (existingRole) {
      // TODO: guardian#128: better error handling
      throw new Error('Role already exists');
    }

    const newRole: RoleResponseData = {
      resource_url: `http://localhost/guardian/management/roleDatas/${roleData.app_name}/${roleData.namespace_name}/${roleData.name}`,
      ...roleData,
    };
    this._db.roles.push(newRole);

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({role: newRole});
      }, this._responseTimeout);
    });
  }

  updateRoleRequest(roleData: RoleRequestData): Promise<RoleResponse> {
    const existingRole = this._db.roles.filter(rl => {
      return (
        rl.app_name === roleData.app_name && rl.namespace_name === roleData.namespace_name && rl.name === roleData.name
      );
    });
    if (existingRole.length === 0) {
      // TODO: guardian#128: better error handling
      throw new Error('Role does not exist');
    }
    const updatedRole = existingRole[0];
    updatedRole.display_name = roleData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({role: updatedRole});
      }, this._responseTimeout);
    });
  }

  fetchContextsRequest(app?: string, namespace?: string): Promise<ContextsResponse> {
    let mockContexts = this._db.contexts;
    if (app !== undefined && app !== '') {
      if (namespace !== undefined && namespace !== '') {
        mockContexts = this._db.contexts.filter(context => {
          return context.app_name === app && context.namespace_name === namespace;
        });
      } else {
        mockContexts = this._db.contexts.filter(context => {
          return context.app_name === app;
        });
      }
    }

    const mockContextsResponse: ContextsResponse = makeMockContextsResponse(mockContexts);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockContextsResponse);
      }, this._responseTimeout);
    });
  }

  fetchContextRequest(app: string, namespace: string, name: string): Promise<ContextResponse> {
    const mockContext: ContextResponseData[] = this._db.contexts.filter(context => {
      return context.app_name === app && context.namespace_name == namespace && context.name === name;
    });
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({context: mockContext[0]});
      }, this._responseTimeout);
    });
  }

  createContextRequest(contextData: ContextRequestData): Promise<ContextResponse> {
    const existingContext =
      this._db.contexts.filter(ctx => {
        return (
          ctx.app_name === contextData.app_name &&
          ctx.namespace_name === contextData.namespace_name &&
          ctx.name === contextData.name
        );
      }).length !== 0;
    if (existingContext) {
      // TODO: guardian#128: better error handling
      throw new Error('Context already exists');
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
        resolve({context: newContext});
      }, this._responseTimeout);
    });
  }

  updateContextRequest(contextData: ContextRequestData): Promise<ContextResponse> {
    const existingContext = this._db.contexts.filter(ctx => {
      return (
        ctx.app_name === contextData.app_name &&
        ctx.namespace_name === contextData.namespace_name &&
        ctx.name === contextData.name
      );
    });
    if (existingContext.length === 0) {
      // TODO: guardian#128: better error handling
      throw new Error('Context does not exist');
    }
    const updatedContext = existingContext[0];
    updatedContext.display_name = contextData.display_name;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({context: updatedContext});
      }, this._responseTimeout);
    });
  }

  fetchPermissionsRequest(app: string, namespace: string): Promise<PermissionsResponse> {
    const mockPermissions: PermissionResponseData[] = this._db.permissions.filter(permission => {
      return permission.app_name === app && permission.namespace_name === namespace;
    });

    const mockPermissionsResponse: PermissionsResponse = makeMockPermissionsResponse(mockPermissions);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockPermissionsResponse);
      }, this._responseTimeout);
    });
  }

  fetchConditionsRequest(): Promise<ConditionsResponse> {
    const mockConditionsResponse: ConditionsResponse = makeMockConditionsResponse(this._db.conditions);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockConditionsResponse);
      }, this._responseTimeout);
    });
  }

  fetchCapabilitiesRequest(roleData: CapabilityRoleRequestData): Promise<CapabilitiesResponse> {
    const mockCapabilities: CapabilityResponseData[] = this._db.capabilities.filter(capability => {
      return (
        capability.role.app_name === roleData.app_name &&
        capability.role.namespace_name === roleData.namespace_name &&
        capability.role.name === roleData.name
      );
    });

    const mockCapabilitiesResponse: CapabilitiesResponse = makeMockCapabilitiesResponse(mockCapabilities);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(mockCapabilitiesResponse);
      }, this._responseTimeout);
    });
  }

  fetchCapabilityRequest(app: string, namespace: string, name: string): Promise<CapabilityResponse> {
    const mockCapability: CapabilityResponseData[] = this._db.capabilities.filter(capability => {
      return capability.app_name === app && capability.namespace_name == namespace && capability.name === name;
    });
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({capability: mockCapability[0]});
      }, this._responseTimeout);
    });
  }

  createCapabilityRequest(capabilityData: NewCapabilityRequestData): Promise<CapabilityResponse> {
    const existingCapability =
      this._db.capabilities.filter(cap => {
        return (
          cap.app_name === capabilityData.app_name &&
          cap.namespace_name === capabilityData.namespace_name &&
          cap.name === capabilityData.name
        );
      }).length !== 0;
    if (existingCapability) {
      // TODO: guardian#128: better error handling
      throw new Error('Capability already exists');
    }

    const name: string = capabilityData.name ?? uuid4();

    const newCapability: CapabilityResponseData = {
      app_name: capabilityData.app_name,
      namespace_name: capabilityData.namespace_name,
      name: name,
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
        resolve({capability: newCapability});
      }, this._responseTimeout);
    });
  }

  updateCapabilityRequest(capabilityData: CapabilityRequestData): Promise<CapabilityResponse> {
    const existingCapability = this._db.capabilities.filter(cap => {
      return (
        cap.app_name === capabilityData.app_name &&
        cap.namespace_name === capabilityData.namespace_name &&
        cap.name === capabilityData.name
      );
    });
    if (existingCapability.length === 0) {
      // TODO: guardian#128: better error handling
      throw new Error('Capability does not exist');
    }
    const updatedCapability = existingCapability[0];
    updatedCapability.display_name = capabilityData.display_name;
    updatedCapability.relation = capabilityData.relation;
    updatedCapability.conditions = capabilityData.conditions;
    updatedCapability.permissions = capabilityData.permissions;
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({capability: updatedCapability});
      }, this._responseTimeout);
    });
  }

  removeCapabilityRequest(app: string, namespace: string, name: string): Promise<{}> {
    const existingCapability = this._db.capabilities.filter(cap => {
      return cap.app_name === app && cap.namespace_name === namespace && cap.name === name;
    });
    if (existingCapability.length === 0) {
      // TODO: guardian#128: better error handling
      throw new Error('Capability does not exist');
    }

    const index = this._db.capabilities.indexOf(existingCapability[0]);
    this._db.capabilities.splice(index, 1);

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({});
      }, this._responseTimeout);
    });
  }
}
