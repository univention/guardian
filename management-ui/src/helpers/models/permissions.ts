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
