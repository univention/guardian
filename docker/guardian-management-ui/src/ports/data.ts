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
import type {FetchObjectError, Result, SaveError} from '@/adapters/data';

export const dataPortSetting = 'managementUi.adapter.dataPort';

export interface DataPort {
  fetchApps(): Promise<Result<WrappedAppsList, string>>;

  fetchNamespaces(app?: string): Promise<Result<WrappedNamespacesList, string>>;
  fetchNamespace(app: string, name: string): Promise<Result<WrappedNamespace, FetchObjectError>>;
  createNamespace(namespace: Namespace): Promise<Result<WrappedNamespace, SaveError>>;
  updateNamespace(namespace: Namespace): Promise<Result<WrappedNamespace, SaveError>>;

  fetchRoles(app?: string, namespace?: string): Promise<Result<WrappedRolesList, string>>;
  fetchRole(app: string, namespace: string, name: string): Promise<Result<WrappedRole, FetchObjectError>>;
  createRole(role: Role): Promise<Result<WrappedRole, SaveError>>;
  updateRole(role: Role): Promise<Result<WrappedRole, SaveError>>;

  fetchContexts(app?: string, namespace?: string): Promise<Result<WrappedContextsList, string>>;
  fetchContext(app: string, namespace: string, name: string): Promise<Result<WrappedContext, FetchObjectError>>;
  createContext(context: Context): Promise<Result<WrappedContext, SaveError>>;
  updateContext(context: Context): Promise<Result<WrappedContext, SaveError>>;

  fetchCapabilities(
    role: CapabilityRole,
    app?: string,
    namespace?: string
  ): Promise<Result<WrappedCapabilitiesList, string>>;
  fetchCapability(app: string, namespace: string, name: string): Promise<Result<WrappedCapability, FetchObjectError>>;
  createCapability(capability: NewCapability): Promise<Result<WrappedCapability, SaveError>>;
  updateCapability(capability: Capability): Promise<Result<WrappedCapability, SaveError>>;
  removeCapability(app: string, namespace: string, name: string): Promise<Result<null, string>>;

  fetchPermissions(app: string, namespace: string): Promise<Result<WrappedPermissionsList, string>>;

  fetchConditions(): Promise<Result<WrappedConditionsList, string>>;
}
