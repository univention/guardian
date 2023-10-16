import type {AddViewConfig} from '@/helpers/models';
import type {LabeledValue} from '@/helpers/models';
import i18next from 'i18next';

export const getAddNamespaceViewConfig = (appsOptions: LabeledValue<string>[]): AddViewConfig => {
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
              ],
              [
                {
                  type: 'UInputText',
                  props: {
                    name: 'name',
                    label: i18next.t('configs.addView.field.name'),
                    required: true,
                    access: 'write',
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
            ],
          },
        ],
      },
    ],
  };
};
