import type {AddViewConfig} from '@/helpers/models';

export const addCapabilityViewConfig: AddViewConfig = {
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
                  hint: 'Select App first',
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
                  name: 'displayname',
                  label: 'Displayname',
                  required: false,
                  access: 'write',
                },
              },
              {
                type: 'UInputText',
                props: {
                  name: 'name',
                  label: 'Name',
                  hint: 'Auto-generated if left empty.',
                  required: false,
                },
              },
            ],
            [
              {
                type: 'UMultiInput',
                props: {
                  name: 'conditions',
                  label: 'Conditions',
                  required: false,
                  subElements: [
                    {
                      type: 'UExtendingInput',
                      props: {
                        name: 'conditions2',
                        label: '',
                        extensions: {},
                        rootElement: {
                          type: 'UComboBox',
                          props: {
                            name: 'condition',
                            label: 'Condition',
                            options: [
                              {
                                label: 'Condition 1',
                                value: 'condition1',
                              },
                              {
                                label: 'Condition 2',
                                value: 'condition2',
                              },
                            ],
                          },
                        },
                      },
                    },
                  ],
                },
              },
            ],
            [
              {
                type: 'UComboBox',
                props: {
                  name: 'relation',
                  label: 'Realtion',
                  options: [
                    {
                      label: 'AND',
                      value: 'and',
                    },
                    {
                      label: 'OR',
                      value: 'or',
                    },
                  ],
                },
              },
            ],
            [
              {
                type: 'UMultiInput',
                props: {
                  name: 'permissions',
                  label: 'Permissions',
                  hint: 'Select Namespace first',
                  required: true,
                  subElements: [
                    {
                      type: 'UComboBox',
                      props: {
                        name: 'permission',
                        label: 'Permission',
                        options: [],
                      },
                    },
                  ],
                },
              },
            ],
          ],
        },
      ],
    },
  ],
};
