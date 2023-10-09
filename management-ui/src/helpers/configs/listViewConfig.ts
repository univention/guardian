import type {ListViewConfigs} from '@/helpers/models';

export const listViewConfig: ListViewConfigs = {
  role: {
    allowedGlobalActions: ['add'],
    searchForm: [
      {
        type: 'UComboBox',
        props: {
          name: 'appSelection',
          label: 'App',
          options: [
            {
              label: 'All',
              value: '',
            },
          ],
        },
      },
      {
        type: 'UComboBox',
        props: {
          name: 'namespaceSelection',
          label: 'Namespace',
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
        label: 'Name',
        attribute: 'name',
        sorting: 'asc',
      },
      {
        label: 'Displayname',
        attribute: 'displayname',
      },
      {
        label: 'App',
        attribute: 'app',
      },
      {
        label: 'Namespace',
        attribute: 'namespace',
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
          label: 'App',
          options: [
            {
              label: 'All',
              value: '',
            },
          ],
        },
      },
      {
        type: 'UComboBox',
        props: {
          name: 'namespaceSelection',
          label: 'Namespace',
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
        label: 'Name',
        attribute: 'name',
        sorting: 'asc',
      },
      {
        label: 'Displayname',
        attribute: 'displayname',
      },
      {
        label: 'App',
        attribute: 'app',
      },
      {
        label: 'Namespace',
        attribute: 'namespace',
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
          label: 'App',
          options: [
            {
              label: 'All',
              value: '',
            },
          ],
        },
      },
    ],
    searchFormValues: {
      appSelection: '',
    },
    columns: [
      {
        label: 'Name',
        attribute: 'name',
        sorting: 'asc',
      },
      {
        label: 'Displayname',
        attribute: 'displayname',
      },
      {
        label: 'App',
        attribute: 'app',
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
          label: 'App',
          options: [
            {
              label: 'All',
              value: '',
            },
          ],
        },
      },
      {
        type: 'UComboBox',
        props: {
          name: 'namespaceSelection',
          label: 'Namespace',
          options: [],
        },
      },
    ],
    searchFormValues: {
      appSelection: '',
      namespaceSelection: 'all',
    },
    columns: [
      {
        label: 'Name',
        attribute: 'name',
        sorting: 'asc',
      },
      {
        label: 'Displayname',
        attribute: 'displayname',
      },
      {
        label: 'App',
        attribute: 'app',
      },
      {
        label: 'Namespace',
        attribute: 'namespace',
      },
    ],
  },
};
