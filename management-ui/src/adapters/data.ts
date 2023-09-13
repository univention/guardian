import type {DataPort} from '@/ports/data';
import type {WrappedAppsList} from '@/helpers/models/apps';
import type {Namespace, WrappedNamespace, WrappedNamespacesList} from '@/helpers/models/namespaces';
import type {Role, WrappedRole, WrappedRolesList} from '@/helpers/models/roles';
import type {Context, WrappedContext, WrappedContextsList} from '@/helpers/models/contexts';
import type {
  Capability,
  CapabilityRole,
  NewCapability,
  WrappedCapability,
  WrappedCapabilitiesList,
} from '@/helpers/models/capabilities';
import type {WrappedPermissionsList} from '@/helpers/models/permissions';
import type {WrappedConditionsList} from '@/helpers/models/conditions';

export class InMemoryDataAdapter implements DataPort {
  fetchApps(): Promise<WrappedAppsList> {
    return new Promise(resolve => {
      resolve({
        apps: [
          {
            name: 'app-1',
            displayName: 'App 1',
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchNamespaces(app?: string): Promise<WrappedNamespacesList> {
    console.log(`app: ${app}`);
    return new Promise(resolve => {
      resolve({
        namespaces: [
          {
            appName: 'app-1',
            name: 'namespace-1',
            displayName: 'Namespace 1',
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchNamespace(app: string, name: string): Promise<WrappedNamespace> {
    console.log(`app: ${app}; name: ${name}`);
    return new Promise(resolve => {
      resolve({
        namespace: {
          appName: 'app-1',
          name: 'namespace-1',
          displayName: 'Namespace 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  createNamespace(namespace: Namespace): Promise<WrappedNamespace> {
    console.log(namespace);
    return new Promise(resolve => {
      resolve({
        namespace: {
          appName: 'app-1',
          name: 'namespace-1',
          displayName: 'Namespace 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  updateNamespace(namespace: Namespace): Promise<WrappedNamespace> {
    console.log(namespace);
    return new Promise(resolve => {
      resolve({
        namespace: {
          appName: 'app-1',
          name: 'namespace-1',
          displayName: 'Namespace 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  fetchRoles(app?: string, namespace?: string): Promise<WrappedRolesList> {
    console.log(`app: ${app}; namespace: ${namespace}`);
    return new Promise(resolve => {
      resolve({
        roles: [
          {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'role-1',
            displayName: 'Role 1',
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchRole(app: string, namespace: string, name: string): Promise<WrappedRole> {
    console.log(`app: ${app}; namespace: ${namespace}; name: ${name}`);
    return new Promise(resolve => {
      resolve({
        role: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'role-1',
          displayName: 'Role 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  createRole(role: Role): Promise<WrappedRole> {
    console.log(role);
    return new Promise(resolve => {
      resolve({
        role: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'role-1',
          displayName: 'Role 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  updateRole(role: Role): Promise<WrappedRole> {
    console.log(role);
    return new Promise(resolve => {
      resolve({
        role: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'role-1',
          displayName: 'Role 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  fetchContexts(app?: string, namespace?: string): Promise<WrappedContextsList> {
    console.log(`app: ${app}; namespace: ${namespace}`);
    return new Promise(resolve => {
      resolve({
        contexts: [
          {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'context-1',
            displayName: 'Context 1',
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchContext(app: string, namespace: string, name: string): Promise<WrappedContext> {
    console.log(`app: ${app}; namespace: ${namespace}; name: ${name}`);
    return new Promise(resolve => {
      resolve({
        context: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'context-1',
          displayName: 'Context 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  createContext(context: Context): Promise<WrappedContext> {
    console.log(context);
    return new Promise(resolve => {
      resolve({
        context: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'context-1',
          displayName: 'Context 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  updateContext(context: Context): Promise<WrappedContext> {
    console.log(context);
    return new Promise(resolve => {
      resolve({
        context: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'context-1',
          displayName: 'Context 1',
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  fetchCapabilities(role: CapabilityRole, app?: string, namespace?: string): Promise<WrappedCapabilitiesList> {
    console.log(`role: ${role}; app: ${app}; namespace: ${namespace}`);
    return new Promise(resolve => {
      resolve({
        capabilities: [
          {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'capability-1',
            displayName: 'Capability 1',
            role: {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'role-1',
            },
            conditions: [
              {
                appName: 'app-1',
                namespaceName: 'namespace-1',
                name: 'condition-1',
                parameters: [
                  {
                    name: 'parameter-1',
                    value: 'value-1',
                  },
                ],
              },
            ],
            relation: 'AND',
            permissions: [
              {
                appName: 'app-1',
                namespaceName: 'namespace-1',
                name: 'permission-1',
              },
            ],
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchCapability(app: string, namespace: string, name: string): Promise<WrappedCapability> {
    console.log(`app: ${app}; namespace: ${namespace}; name: ${name}`);
    return new Promise(resolve => {
      resolve({
        capability: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'capability-1',
          displayName: 'Capability 1',
          role: {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'role-1',
          },
          conditions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'condition-1',
              parameters: [
                {
                  name: 'parameter-1',
                  value: 'value-1',
                },
              ],
            },
          ],
          relation: 'AND',
          permissions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'permission-1',
            },
          ],
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  createCapability(capability: NewCapability): Promise<WrappedCapability> {
    console.log(capability);
    return new Promise(resolve => {
      resolve({
        capability: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'capability-1',
          displayName: 'Capability 1',
          role: {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'role-1',
          },
          conditions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'condition-1',
              parameters: [
                {
                  name: 'parameter-1',
                  value: 'value-1',
                },
              ],
            },
          ],
          relation: 'AND',
          permissions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'permission-1',
            },
          ],
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  updateCapability(capability: Capability): Promise<WrappedCapability> {
    console.log(capability);
    return new Promise(resolve => {
      resolve({
        capability: {
          appName: 'app-1',
          namespaceName: 'namespace-1',
          name: 'capability-1',
          displayName: 'Capability 1',
          role: {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'role-1',
          },
          conditions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'condition-1',
              parameters: [
                {
                  name: 'parameter-1',
                  value: 'value-1',
                },
              ],
            },
          ],
          relation: 'AND',
          permissions: [
            {
              appName: 'app-1',
              namespaceName: 'namespace-1',
              name: 'permission-1',
            },
          ],
          resourceUrl: 'http://fake.url',
        },
      });
    });
  }

  removeCapability(app: string, namespace: string, name: string): Promise<boolean> {
    console.log(`app: ${app}; namespace: ${namespace}; name: ${name}`);
    return new Promise(resolve => {
      resolve(true);
    });
  }

  fetchPermissions(app: string, namespace: string): Promise<WrappedPermissionsList> {
    console.log(`app: ${app}; namespace: ${namespace}`);
    return new Promise(resolve => {
      resolve({
        permissions: [
          {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'permission-1',
            displayName: 'Permission 1',
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }

  fetchConditions(): Promise<WrappedConditionsList> {
    return new Promise(resolve => {
      resolve({
        conditions: [
          {
            appName: 'app-1',
            namespaceName: 'namespace-1',
            name: 'condition-1',
            displayName: 'Condition 1',
            documentation: 'Documentation for condition-1',
            parameters: [
              {
                name: 'parameter-1',
              },
            ],
            resourceUrl: 'http://fake.url',
          },
        ],
      });
    });
  }
}
