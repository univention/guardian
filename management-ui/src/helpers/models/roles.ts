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
