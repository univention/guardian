import type {PaginationResponseData} from '@/helpers/models/pagination';

export interface AppResponseData {
  name: string;
  display_name: string;
  resource_url: string;
}

export interface AppsResponse {
  pagination: PaginationResponseData;
  apps: AppResponseData[];
}

export interface DisplayApp {
  name: string;
  displayName: string;
  resourceUrl: string;
}

export interface WrappedAppsList {
  apps: DisplayApp[];
}
