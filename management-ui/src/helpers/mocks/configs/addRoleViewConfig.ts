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
    /*
    {
      label: 'Capabilities',
      name: 'capabilities',
      fieldsets: [
        {
          label: 'Capability mapping',
          name: 'capabilities__mapping',
          rows: [
            [
              {
                type: 'UMultiInput',
                props: {
                  name: 'mapping',
                  label: 'Mapping',
                  required: false,
                  subElements: [
                    {
                      type: 'UMultiInput',
                      props: {
                        name: 'conditions',
                        label: 'Conditions',
                        required: false,
                        subElements: [
                          {
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
                        ],
                      },
                    },
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
                    {
                      type: 'UMultiInput',
                      props: {
                        name: 'permissions',
                        label: 'Permissions',
                        required: false,
                        subElements: [
                          {
                            type: 'UComboBox',
                            props: {
                              name: 'permission',
                              label: 'Permission',
                              options: [
                                {
                                  label: 'Permission 1',
                                  value: 'permission1',
                                },
                                {
                                  label: 'Permission 2',
                                  value: 'permission2',
                                },
                              ],
                            },
                          },
                        ],
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
    */
  ],
};
