import type {ListResponseModel} from '@/helpers/models';

/* eslint-disable camelcase */
export const capabilitiesListResponseModel: ListResponseModel = {
  id: 'capability1',
  allowedActions: ['edit', 'delete'],
  attributes: {
    name: {
      value: 'capability1',
      access: 'read',
    },
    displayname: {
      value: 'Capability 1',
      access: 'read',
    },
    app: {
      value: 'App1',
      access: 'read',
    },
    namespace: {
      value: 'namespace1',
      access: 'read',
    },
  },
};
/* eslint-enable camelcase */
