import type {DetailResponseModel, FormValues} from '@/helpers/models';
import i18next from 'i18next';

export const getNamespaceDetailResponseModel = (values: FormValues): DetailResponseModel => {
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
            ],
          },
        ],
      },
    ],
    values,
  };
};
