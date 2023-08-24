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
              value: 'all',
            },
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
          name: 'namespaceSelection',
          label: 'Namespace',
          options: [], // options fetched in ListView.vue dependent on 'appSelection'
        },
      },
      /*
      // Removed for now. The Management API does not support searching in the fields of the roles for now.
      // And maybe it won't
      {
        type: 'UInputText',
        props: {
          name: 'freeSearch',
          label: 'Search',
        },
      },
      */
    ],
    searchFormValues: {
      appSelection: 'all',
      namespaceSelection: '', // value will be set in ListView.vue
      // freeSearch: '',
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
              value: 'all',
            },
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
          name: 'namespaceSelection',
          label: 'Namespace',
          options: [],
        },
      },
      /*
      {
        type: 'UInputText',
        props: {
          name: 'freeSearch',
          label: 'Search',
        },
      },
      */
    ],
    searchFormValues: {
      appSelection: 'all',
      namespaceSelection: 'all',
      // freeSearch: '',
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
              value: 'all',
            },
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
      /*
      {
        type: 'UInputText',
        props: {
          name: 'freeSearch',
          label: 'Search',
        },
      },
      */
    ],
    searchFormValues: {
      appSelection: 'all',
      // freeSearch: '',
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
};
