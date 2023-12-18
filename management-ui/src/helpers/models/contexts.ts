import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface ContextRequestData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
}

export interface ContextResponseData {
  app_name: string;
  namespace_name: string;
  name: string;
  display_name: string;
  resource_url: string;
}

export interface ContextResponse {
  context: ContextResponseData;
}

export interface ContextsResponse {
  pagination: PaginationResponseData;
  contexts: ContextResponseData[];
}

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
