import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface NamespaceRequestData {
  app_name: string;
  name: string;
  display_name: string;
}

export interface NamespaceResponseData {
  app_name: string;
  name: string;
  display_name: string;
  resource_url: string;
}

export interface NamespaceResponse {
  namespace: NamespaceResponseData;
}

export interface NamespacesResponse {
  pagination: PaginationResponseData;
  namespaces: NamespaceResponseData[];
}

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
