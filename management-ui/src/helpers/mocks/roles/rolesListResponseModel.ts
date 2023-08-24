import type {ListResponseModel} from '@/helpers/models';

/* eslint-disable camelcase */
export const rolesListResponseModel: ListResponseModel = {
  id: 'role1',
  allowedActions: ['edit'],
  attributes: {
    name: {
      value: 'role1',
      access: 'read',
    },
    displayname: {
      value: 'Role 1',
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
