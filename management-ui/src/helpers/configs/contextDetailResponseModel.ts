import type {DetailResponseModel} from '@/helpers/models';

export const contextDetailResponseModel: DetailResponseModel = {
  url: '',
  allowedActions: ['save'],
  pages: [
    {
      label: 'General',
      name: 'general',
      fieldsets: [
        {
          label: 'Basic settings',
          name: 'general__basicSettings',
          rows: [
            [
              {
                type: 'UInputText',
                props: {
                  name: 'appName',
                  label: 'App name',
                  access: 'read',
                },
              },
              {
                type: 'UInputText',
                props: {
                  name: 'namespaceName',
                  label: 'Namespace name',
                  required: true,
                  access: 'read',
                },
              },
            ],
            [
              {
                type: 'UInputText',
                props: {
                  name: 'name',
                  label: 'Name',
                  required: true,
                  access: 'read',
                },
              },
              {
                type: 'UInputText',
                props: {
                  name: 'displayName',
                  label: 'Displayname',
                  required: false,
                  access: 'write',
                },
              },
            ],
          ],
        },
      ],
    },
  ],
  values: {
    appName: '',
    namespaceName: '',
    name: '',
    displayName: '',
  },
};
