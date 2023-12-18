import type {AddViewConfig} from '@/helpers/models';
import type {LabeledValue} from '@/helpers/models';
import i18next from 'i18next';
import {validateName} from '@/helpers/validators';

export const getAddContextViewConfig = (appsOptions: LabeledValue<string>[]): AddViewConfig => {
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
                    name: 'name',
                    label: i18next.t('configs.addView.field.name'),
                    required: true,
                    access: 'write',
                    validators: [v => validateName(v)],
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
