export interface Context {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
}

export interface DisplayContext {
  appName: string;
  namespaceName: string;
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedContext {
  context: DisplayContext;
}

export interface WrappedContextsList {
  contexts: DisplayContext[];
}
