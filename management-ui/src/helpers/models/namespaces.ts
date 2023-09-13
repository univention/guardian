export interface Namespace {
  appName: string;
  name: string;
  displayName: string;
}

export interface DisplayNamespace {
  appName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedNamespace {
  namespace: DisplayNamespace;
}

export interface WrappedNamespacesList {
  namespaces: DisplayNamespace[];
}
