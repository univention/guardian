import type {ListViewConfigs} from '@/helpers/models';
import i18next from 'i18next';
import type {LabeledValue} from '@/helpers/models';

export const getListViewConfig = (appsOptions: LabeledValue<string>[]): ListViewConfigs => {
  return {
    role: {
      allowedGlobalActions: ['add'],
      searchForm: [
        {
          type: 'UComboBox',
          props: {
            name: 'appSelection',
            label: i18next.t('configs.listView.searchForm.appSelection'),
            options: appsOptions,
          },
        },
        {
          type: 'UComboBox',
          props: {
            name: 'namespaceSelection',
            label: i18next.t('configs.listView.searchForm.namespaceSelection'),
            options: [], // options fetched in ListView.vue dependent on 'appSelection'
          },
        },
      ],
      searchFormValues: {
        appSelection: '',
        namespaceSelection: '', // value will be set in ListView.vue
      },
      columns: [
        {
          label: i18next.t('configs.listView.columns.name'),
          attribute: 'name',
          sorting: 'asc',
        },
        {
          label: i18next.t('configs.listView.columns.displayName'),
          attribute: 'displayName',
        },
        {
          label: i18next.t('configs.listView.columns.appName'),
          attribute: 'appName',
        },
        {
          label: i18next.t('configs.listView.columns.namespaceName'),
          attribute: 'namespaceName',
        },
      ],
    },
    context: {
      allowedGlobalActions: ['add'],
      searchForm: [
        {
          type: 'UComboBox',
          props: {
            name: 'appSelection',
            label: i18next.t('configs.listView.searchForm.appSelection'),
            options: appsOptions,
          },
        },
        {
          type: 'UComboBox',
          props: {
            name: 'namespaceSelection',
            label: i18next.t('configs.listView.searchForm.namespaceSelection'),
            options: [],
          },
        },
      ],
      searchFormValues: {
        appSelection: '',
        namespaceSelection: '',
      },
      columns: [
        {
          label: i18next.t('configs.listView.columns.name'),
          attribute: 'name',
          sorting: 'asc',
        },
        {
          label: i18next.t('configs.listView.columns.displayName'),
          attribute: 'displayName',
        },
        {
          label: i18next.t('configs.listView.columns.appName'),
          attribute: 'appName',
        },
        {
          label: i18next.t('configs.listView.columns.namespaceName'),
          attribute: 'namespaceName',
        },
      ],
    },
    namespace: {
      allowedGlobalActions: ['add'],
      searchForm: [
        {
          type: 'UComboBox',
          props: {
            name: 'appSelection',
            label: i18next.t('configs.listView.searchForm.appSelection'),
            options: appsOptions,
          },
        },
      ],
      searchFormValues: {
        appSelection: '',
      },
      columns: [
        {
          label: i18next.t('configs.listView.columns.name'),
          attribute: 'name',
          sorting: 'asc',
        },
        {
          label: i18next.t('configs.listView.columns.displayName'),
          attribute: 'displayName',
        },
        {
          label: i18next.t('configs.listView.columns.appName'),
          attribute: 'appName',
        },
      ],
    },
    capability: {
      allowedGlobalActions: ['add'],
      searchForm: [
        {
          type: 'UComboBox',
          props: {
            name: 'appSelection',
            label: i18next.t('configs.listView.searchForm.appSelection'),
            options: appsOptions,
          },
        },
        {
          type: 'UComboBox',
          props: {
            name: 'namespaceSelection',
            label: i18next.t('configs.listView.searchForm.namespaceSelection'),
            options: [],
          },
        },
      ],
      searchFormValues: {
        appSelection: '',
        namespaceSelection: '',
      },
      columns: [
        {
          label: i18next.t('configs.listView.columns.name'),
          attribute: 'name',
          sorting: 'asc',
        },
        {
          label: i18next.t('configs.listView.columns.displayName'),
          attribute: 'displayName',
        },
        {
          label: i18next.t('configs.listView.columns.appName'),
          attribute: 'appName',
        },
        {
          label: i18next.t('configs.listView.columns.namespaceName'),
          attribute: 'namespaceName',
        },
      ],
    },
  };
};
