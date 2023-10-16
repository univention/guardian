import type {AddViewConfig, Field} from '@/helpers/models';
import type {LabeledValue} from '@/helpers/models';
import i18next from 'i18next';

export const getAddCapabilityViewConfig = (
  appsOptions: LabeledValue<string>[],
  conditionsElement: Field
): AddViewConfig => {
  return {
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
                  type: 'UComboBox',
                  props: {
                    name: 'appName',
                    label: i18next.t('configs.addView.field.appName'),
                    required: true,
                    access: 'write',
                    options: appsOptions,
                  },
                },
                {
                  type: 'UComboBox',
                  props: {
                    name: 'namespaceName',
                    label: i18next.t('configs.addView.field.namespaceName'),
                    hint: i18next.t('configs.addView.hint.selectAppFirst'),
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
                    name: 'displayName',
                    label: i18next.t('configs.addView.field.displayName'),
                    required: false,
                    access: 'write',
                  },
                },
                {
                  type: 'UInputText',
                  props: {
                    name: 'name',
                    label: i18next.t('configs.addView.field.name'),
                    hint: i18next.t('configs.addView.hint.autoGenerate'),
                    required: false,
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
                    hint: i18next.t('configs.addView.hint.selectNamespaceFirst'),
                    required: true,
                    subElements: [
                      {
                        type: 'UComboBox',
                        props: {
                          name: 'permission',
                          label: i18next.t('configs.addView.field.permissions'),
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
};
