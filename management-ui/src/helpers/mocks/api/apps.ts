import {type AppResponseData, type AppsResponse} from '@/helpers/models/apps';
import {type PaginationResponseData} from '@/helpers/models/pagination';
import {getPagination} from '@/helpers/mocks/api/pagination';

export const makeMockApps = (): AppResponseData[] => {
  const numApps: number = 100;
  const apps: AppResponseData[] = [];
  for (let x = 1; x <= numApps; x++) {
    apps.push({
      name: `app-${x}`,
      display_name: `App ${x}`,
      resource_url: `https://localhost/guardian/management/apps/app-${x}`,
    });
  }
  return apps;
};

export const makeMockAppsResponse = (apps: AppResponseData[]): AppsResponse => {
  const pagination: PaginationResponseData = getPagination(apps.length);
  return {
    pagination: pagination,
    apps: apps,
  };
};
