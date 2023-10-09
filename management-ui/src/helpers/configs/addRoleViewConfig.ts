import type {AddViewConfig} from '@/helpers/models';

export const addRoleViewConfig: AddViewConfig = {
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
                  options: [],
                },
              },
              {
                type: 'UComboBox',
                props: {
                  name: 'namespaceName',
                  label: 'Namespace name',
                  required: true,
                  access: 'write',
                  options: [],
                },
              },
            ],
            [
              {
                type: 'UInputText',
                props: {
                  // TODO fastapi schema validator for frontend?
                  name: 'name',
                  label: 'Name',
                  required: true,
                  access: 'write',
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
};
