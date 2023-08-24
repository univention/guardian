import type {DetailResponseModel} from '@/helpers/models';

export const roleDetailResponseModel: DetailResponseModel = {
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
  values: {
    appName: 'App 1',
    namespaceName: 'Namespace 1',
    name: 'name',
    displayname: 'display name',
    // mapping: [[[['condition1']], 'or', [['permission1']]]],
  },
};
