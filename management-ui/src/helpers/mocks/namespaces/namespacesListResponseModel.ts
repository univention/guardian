import type {ListResponseModel} from '@/helpers/models';

/* eslint-disable camelcase */
export const namespacesListResponseModel: ListResponseModel = {
  id: 'role1',
  allowedActions: ['edit'],
  attributes: {
    name: {
      value: 'namespace1',
      access: 'read',
    },
    displayname: {
      value: 'Namespace 1',
      access: 'read',
    },
    app: {
      value: 'App1',
      access: 'read',
    },
  },
};
/* eslint-enable camelcase */
