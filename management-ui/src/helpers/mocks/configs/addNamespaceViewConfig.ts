import type {AddViewConfig} from '@/helpers/models';

export const addNamespaceViewConfig: AddViewConfig = {
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
                type: 'UComboBox',
                props: {
                  name: 'appName',
                  label: 'App name',
                  required: true,
                  access: 'write',
                  options: [
                    {
                      label: 'App 1',
                      value: 'app1',
                    },
                    {
                      label: 'App 2',
                      value: 'app2',
                    },
                  ],
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
                  access: 'write',
                },
              },
              {
                type: 'UInputText',
                props: {
                  name: 'displayname',
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
};
