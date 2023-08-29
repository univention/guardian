import {useAdapterStore} from '@/stores/adapter';
import {useSettingsStore} from '@/stores/settings';
import i18next from 'i18next';

const buildOptions = async function (options: RequestInit, minTokenValidity = 30): Promise<RequestInit> {
  const settingsStore = useSettingsStore();
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);
  const authenticationAdapter = adapterStore.authenticationAdapter;
  const authHeader = await authenticationAdapter.getValidAuthorizationHeader(minTokenValidity);
  const defaultHeaders = {'Accept-Language': i18next.language, accept: 'application/json'};
  if (options.headers !== undefined) {
    options.headers = {...defaultHeaders, ...options.headers, ...authHeader};
  } else {
    options.headers = {...defaultHeaders, ...authHeader};
  }
  return options;
};

export const fetchAuthenticated = async function (resource: RequestInfo, options = {}): Promise<Response> {
  let updatedOptions = await buildOptions(options);
  let fetchPromise = fetch(resource, updatedOptions);
  const result = await fetchPromise;
  if (result.status === 401) {
    updatedOptions = await buildOptions(options, -1);
    fetchPromise = fetch(resource, updatedOptions);
  }
  return fetchPromise;
};
