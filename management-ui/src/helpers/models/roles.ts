import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface RoleRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
}

export interface RoleResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  resource_url: string;
}

export interface RoleResponse {
  role: RoleResponseData;
}

export interface RolesResponse {
  pagination: PaginationResponseData;
  roles: RoleResponseData[];
}

export interface Role {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
}

export interface DisplayRole {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedRole {
  role: DisplayRole;
}

export interface WrappedRolesList {
  roles: DisplayRole[];
}
