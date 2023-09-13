export interface DisplayApp {
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedAppsList {
  apps: DisplayApp[];
}
