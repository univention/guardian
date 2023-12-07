import type {DetailResponseModel, Field, FormValues, LabeledValue} from '@/helpers/models';
import i18next from 'i18next';

export const getCapabilityDetailResponseModel = (
  values: FormValues,
  conditionsElement: Field,
  permissionsOptions: LabeledValue<string>[]
): DetailResponseModel => {
  return {
    url: '',
    allowedActions: ['save'],
    pages: [
      {
        label: i18next.t('configs.addView.page.general'),
        name: 'general',
        fieldsets: [
          {
            label: i18next.t('configs.addView.fieldset.basicSettings'),
            name: 'general__basicSettings',
            rows: [
              [
                {
                  type: 'UInputText',
                  props: {
                    name: 'appName',
                    label: i18next.t('configs.addView.field.appName'),
                    access: 'read',
                  },
                },
                {
                  type: 'UInputText',
                  props: {
                    name: 'namespaceName',
                    label: i18next.t('configs.addView.field.namespaceName'),
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
                    label: i18next.t('configs.addView.field.name'),
                    access: 'read',
                  },
                },
                {
                  type: 'UInputText',
                  props: {
                    name: 'displayName',
                    label: i18next.t('configs.addView.field.displayName'),
                    required: false,
                    access: 'write',
                  },
                },
              ],
              [
                {
                  type: 'UMultiInput',
                  props: {
                    name: 'conditions',
                    label: i18next.t('configs.addView.field.conditions'),
                    required: false,
                    subElements: [conditionsElement],
                  },
                },
              ],
              [
                {
                  type: 'UComboBox',
                  props: {
                    name: 'relation',
                    label: i18next.t('configs.addView.field.relation'),
                    options: [
                      {
                        label: 'AND',
                        value: 'AND',
                      },
                      {
                        label: 'OR',
                        value: 'OR',
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
                    label: i18next.t('configs.addView.field.permissions'),
                    required: true,
                    subElements: [
                      {
                        type: 'UComboBox',
                        props: {
                          name: 'permission',
                          label: i18next.t('configs.addView.field.permissions'),
                          options: permissionsOptions,
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
    values,
  };
};
