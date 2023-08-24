import type {ListResponseModel} from '@/helpers/models';

/* eslint-disable camelcase */
export const contextsListResponseModel: ListResponseModel = {
  id: 'role1',
  allowedActions: ['edit'],
  attributes: {
    name: {
      value: 'context1',
      access: 'read',
    },
    displayname: {
      value: 'Context 1',
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
