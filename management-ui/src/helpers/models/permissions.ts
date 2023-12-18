import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface PermissionResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  resource_url: string;
}

export interface PermissionsResponse {
  pagination: PaginationResponseData;
  permissions: PermissionResponseData[];
}

export interface Permission {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
}

export interface DisplayPermission {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedPermission {
  permission: DisplayPermission;
}

export interface WrappedPermissionsList {
  permissions: DisplayPermission[];
}
