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

export const dataPortSetting = 'managementUi.adapter.dataPort';

export interface DataPort {
  fetchApps(): Promise<WrappedAppsList>;

  fetchNamespaces(app?: string): Promise<WrappedNamespacesList>;
  fetchNamespace(app: string, name: string): Promise<WrappedNamespace>;
  createNamespace(namespace: Namespace): Promise<WrappedNamespace>;
  updateNamespace(namespace: Namespace): Promise<WrappedNamespace>;

  fetchRoles(app?: string, namespace?: string): Promise<WrappedRolesList>;
  fetchRole(app: string, namespace: string, name: string): Promise<WrappedRole>;
  createRole(role: Role): Promise<WrappedRole>;
  updateRole(role: Role): Promise<WrappedRole>;

  fetchContexts(app?: string, namespace?: string): Promise<WrappedContextsList>;
  fetchContext(app: string, namespace: string, name: string): Promise<WrappedContext>;
  createContext(context: Context): Promise<WrappedContext>;
  updateContext(context: Context): Promise<WrappedContext>;

  fetchCapabilities(role: CapabilityRole, app?: string, namespace?: string): Promise<WrappedCapabilitiesList>;
  fetchCapability(app: string, namespace: string, name: string): Promise<WrappedCapability>;
  createCapability(capability: NewCapability): Promise<WrappedCapability>;
  updateCapability(capability: Capability): Promise<WrappedCapability>;
  removeCapability(app: string, namespace: string, name: string): Promise<boolean>;

  fetchPermissions(app: string, namespace: string): Promise<WrappedPermissionsList>;

  fetchConditions(): Promise<WrappedConditionsList>;
}
