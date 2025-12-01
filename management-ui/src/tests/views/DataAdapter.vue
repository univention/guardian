<script setup lang="ts">
import {computed, type ComputedRef, onMounted, type Ref, ref, watch} from 'vue';
import {
  SubElement,
  type SubElementProps,
  UButton,
  UComboBox,
  UGrid,
  type UGridColumnDefinition,
  type UGridRow,
  UInputText,
  UMultiInput,
} from '@univention/univention-veb';
import type {DataPort} from '@/ports/data';
import {ApiDataAdapter, type FetchObjectError, InMemoryDataAdapter, type SaveError} from '@/adapters/data';
import {InMemoryAuthenticationAdapter} from '@/adapters/authentication';
import type {DisplayApp} from '@/helpers/models/apps';
import type {DisplayNamespace} from '@/helpers/models/namespaces';
import type {DisplayRole} from '@/helpers/models/roles';
import type {DisplayCondition} from '@/helpers/models/conditions';
import type {DisplayPermission} from '@/helpers/models/permissions';
import type {DisplayCapability} from '@/helpers/models/capabilities';
import {useSettingsStore} from '@/stores/settings';
import {useAdapterStore} from '@/stores/adapter';

const loading = ref(true);
const settingsStore = useSettingsStore();

interface FilterConfig {
  show: boolean;
  required?: boolean;
  access?: 'read' | 'write';
}

interface FilterList {
  app: FilterConfig;
  namespace: FilterConfig;
  name: FilterConfig;
  role: FilterConfig;
}

interface ActionConfig {
  show: boolean;
  disabled?: boolean;
}

interface ActionList {
  getMany: ActionConfig;
  getOne: ActionConfig;
  postOne: ActionConfig;
  putOne: ActionConfig;
  deleteOne: ActionConfig;
}

interface EditFormConfig {
  show: boolean;
  required?: boolean;
  access?: 'read' | 'write';
}

interface EditFormFieldConfig {
  app: EditFormConfig;
  namespace: EditFormConfig;
  name: EditFormConfig;
  displayName: EditFormConfig;
  role: EditFormConfig;
  conditions: EditFormConfig;
  relation: EditFormConfig;
  permissions: EditFormConfig;
}

interface ObjConfig {
  columns: UGridColumnDefinition[];
  filters: FilterList;
  actions: ActionList;
  editForm: EditFormFieldConfig | null;
}

interface Config {
  apps: ObjConfig;
  namespaces: ObjConfig;
  roles: ObjConfig;
  contexts: ObjConfig;
  permissions: ObjConfig;
  conditions: ObjConfig;
  capabilities: ObjConfig;
}

interface FilterState {
  app: string;
  namespace: string;
  name: string;
  role: string;
}

type Relation = 'AND' | 'OR';
interface EditFormValues {
  app: string;
  namespace: string;
  name: string;
  displayName: string;
  role: string;
  conditions: string[][];
  relation: Relation;
  permissions: string[];
}

interface EditFormState {
  mode: 'create' | 'update';
  values: EditFormValues;
}

interface ObjState {
  all: any[];
  selection: string[];
  error: string;
  filters: FilterState;
  editForm: EditFormState;
}

interface State {
  apps: ObjState;
  namespaces: ObjState;
  roles: ObjState;
  contexts: ObjState;
  permissions: ObjState;
  conditions: ObjState;
  capabilities: ObjState;
}

interface Option {
  label: string;
  value: string;
  disabled?: boolean;
}

interface Adapter {
  name: string;
  adapter: DataPort;
  currentTab: 'apps' | 'namespaces' | 'roles' | 'contexts' | 'permissions' | 'conditions' | 'capabilities';
  state: State;
}

interface Attribute {
  value: any;
  access: 'read' | 'write' | 'none';
}

const makeDefaultState = (): State => {
  const makeDefaultObjState = (): ObjState => {
    return {
      all: [],
      selection: [],
      error: '',
      filters: {
        app: '',
        namespace: '',
        name: '',
        role: '',
      },
      editForm: {
        mode: 'create',
        values: {
          app: '',
          namespace: '',
          name: '',
          displayName: '',
          role: '',
          conditions: [],
          relation: 'AND',
          permissions: [],
        },
      },
    };
  };

  return {
    apps: makeDefaultObjState(),
    namespaces: makeDefaultObjState(),
    roles: makeDefaultObjState(),
    contexts: makeDefaultObjState(),
    permissions: makeDefaultObjState(),
    conditions: makeDefaultObjState(),
    capabilities: makeDefaultObjState(),
  };
};

// This controls most display elements
const config: Ref<Config> = ref({
  apps: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
    ],
    filters: {
      app: {show: false},
      namespace: {show: false},
      name: {show: false},
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: false,
      },
      getOne: {show: false},
      postOne: {show: false},
      putOne: {show: false},
      deleteOne: {show: false},
    },
    editForm: null,
  },
  namespaces: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'App', attribute: 'appName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
    ],
    filters: {
      app: {
        show: true,
        required: computed(() => {
          return currentAdapter.value.state.namespaces.filters.name !== '';
        }),
        access: 'write',
      },
      namespace: {show: false},
      name: {
        show: true,
        required: false,
        access: computed(() => {
          return currentAdapter.value.state.namespaces.filters.app === '' ? 'read' : 'write';
        }),
      },
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: computed(() => {
          return currentAdapter.value.state.namespaces.filters.name !== '';
        }),
      },
      getOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.namespaces.filters.app === '' ||
            currentAdapter.value.state.namespaces.filters.name === ''
          );
        }),
      },
      postOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.namespaces.editForm.values.app === '' ||
            currentAdapter.value.state.namespaces.editForm.values.name === ''
          );
        }),
      },
      putOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.namespaces.editForm.values.app === '' ||
            currentAdapter.value.state.namespaces.editForm.values.name === ''
          );
        }),
      },
      deleteOne: {show: false},
    },
    editForm: {
      app: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.namespaces.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      namespace: {show: false},
      name: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.namespaces.editForm.mode === 'create' &&
            currentAdapter.value.state.namespaces.editForm.values.app !== ''
            ? 'write'
            : 'read';
        }),
      },
      displayName: {
        show: true,
        required: false,
        access: 'write',
      },
      role: {show: false},
      conditions: {show: false},
      relation: {show: false},
      permissions: {show: false},
    },
  },
  roles: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'App', attribute: 'appName'},
      {label: 'Namespace', attribute: 'namespaceName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
    ],
    filters: {
      app: {
        show: true,
        required: computed(() => {
          return (
            currentAdapter.value.state.roles.filters.name !== '' ||
            currentAdapter.value.state.roles.filters.namespace !== ''
          );
        }),
        access: 'write',
      },
      namespace: {
        show: true,
        required: computed(() => {
          return currentAdapter.value.state.roles.filters.name !== '';
        }),
        access: computed(() => {
          return currentAdapter.value.state.roles.filters.app === '' ? 'read' : 'write';
        }),
      },
      name: {
        show: true,
        required: false,
        access: computed(() => {
          return currentAdapter.value.state.roles.filters.namespace === '' ? 'read' : 'write';
        }),
      },
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: computed(() => {
          return currentAdapter.value.state.roles.filters.name !== '';
        }),
      },
      getOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.roles.filters.app === '' ||
            currentAdapter.value.state.roles.filters.namespace === '' ||
            currentAdapter.value.state.roles.filters.name === ''
          );
        }),
      },
      postOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.roles.editForm.values.app === '' ||
            currentAdapter.value.state.roles.editForm.values.namespace === '' ||
            currentAdapter.value.state.roles.editForm.values.name === ''
          );
        }),
      },
      putOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.roles.editForm.values.app === '' ||
            currentAdapter.value.state.roles.editForm.values.namespace === '' ||
            currentAdapter.value.state.roles.editForm.values.name === ''
          );
        }),
      },
      deleteOne: {show: false},
    },
    editForm: {
      app: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.roles.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      namespace: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.roles.editForm.mode === 'create' &&
            currentAdapter.value.state.roles.editForm.values.app !== ''
            ? 'write'
            : 'read';
        }),
      },
      name: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.roles.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      displayName: {
        show: true,
        required: false,
        access: 'write',
      },
      role: {show: false},
      conditions: {show: false},
      relation: {show: false},
      permissions: {show: false},
    },
  },
  contexts: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'App', attribute: 'appName'},
      {label: 'Namespace', attribute: 'namespaceName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
    ],
    filters: {
      app: {
        show: true,
        required: computed(() => {
          return (
            currentAdapter.value.state.contexts.filters.name !== '' ||
            currentAdapter.value.state.contexts.filters.namespace !== ''
          );
        }),
        access: 'write',
      },
      namespace: {
        show: true,
        required: computed(() => {
          return currentAdapter.value.state.contexts.filters.name !== '';
        }),
        access: computed(() => {
          return currentAdapter.value.state.contexts.filters.app === '' ? 'read' : 'write';
        }),
      },
      name: {
        show: true,
        required: false,
        access: computed(() => {
          return currentAdapter.value.state.contexts.filters.namespace === '' ? 'read' : 'write';
        }),
      },
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: computed(() => {
          return currentAdapter.value.state.contexts.filters.name !== '';
        }),
      },
      getOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.contexts.filters.app === '' ||
            currentAdapter.value.state.contexts.filters.namespace === '' ||
            currentAdapter.value.state.contexts.filters.name === ''
          );
        }),
      },
      postOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.contexts.editForm.values.app === '' ||
            currentAdapter.value.state.contexts.editForm.values.namespace === '' ||
            currentAdapter.value.state.contexts.editForm.values.name === ''
          );
        }),
      },
      putOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.contexts.editForm.values.app === '' ||
            currentAdapter.value.state.contexts.editForm.values.namespace === '' ||
            currentAdapter.value.state.contexts.editForm.values.name === ''
          );
        }),
      },
      deleteOne: {show: false},
    },
    editForm: {
      app: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.contexts.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      namespace: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.contexts.editForm.mode === 'create' &&
            currentAdapter.value.state.contexts.editForm.values.app !== ''
            ? 'write'
            : 'read';
        }),
      },
      name: {
        show: true,
        access: computed(() => {
          return currentAdapter.value.state.contexts.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      displayName: {
        show: true,
        required: false,
        access: 'write',
      },
      role: {show: false},
      conditions: {show: false},
      relation: {show: false},
      permissions: {show: false},
    },
  },
  permissions: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'App', attribute: 'appName'},
      {label: 'Namespace', attribute: 'namespaceName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
    ],
    filters: {
      app: {
        show: true,
        required: true,
        access: 'write',
      },
      namespace: {
        show: true,
        required: true,
        access: 'write',
      },
      name: {show: false},
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.permissions.filters.app === '' ||
            currentAdapter.value.state.permissions.filters.namespace === ''
          );
        }),
      },
      getOne: {show: false},
      postOne: {show: false},
      putOne: {show: false},
      deleteOne: {show: false},
    },
    editForm: null,
  },
  conditions: {
    columns: [
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'App', attribute: 'appName'},
      {label: 'Namespace', attribute: 'namespaceName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
      {label: 'Documentation', attribute: 'documentation'},
      {label: 'Parameters', attribute: 'parameters'},
    ],
    filters: {
      app: {show: false},
      namespace: {show: false},
      name: {show: false},
      role: {show: false},
    },
    actions: {
      getMany: {
        show: true,
        disabled: false,
      },
      getOne: {show: false},
      postOne: {show: false},
      putOne: {show: false},
      deleteOne: {show: false},
    },
    editForm: null,
  },
  capabilities: {
    columns: [
      {label: 'Display Name', attribute: 'displayName'},
      {label: 'Name', attribute: 'name', sorting: 'asc'},
      {label: 'Role', attribute: 'role'},
      {label: 'App', attribute: 'appName'},
      {label: 'Namespace', attribute: 'namespaceName'},
      {label: 'Resource URL', attribute: 'resourceUrl'},
      {label: 'Conditions', attribute: 'conditions'},
      {label: 'Relation', attribute: 'relation'},
      {label: 'Permissions', attribute: 'permissions'},
    ],
    filters: {
      app: {
        show: true,
        required: computed(() => {
          return (
            currentAdapter.value.state.capabilities.filters.namespace !== '' ||
            currentAdapter.value.state.capabilities.filters.name !== ''
          );
        }),
        access: 'write',
      },
      namespace: {
        show: true,
        required: computed(() => {
          return currentAdapter.value.state.capabilities.filters.name !== '';
        }),
        access: computed(() => {
          return currentAdapter.value.state.capabilities.filters.app === '' ? 'read' : 'write';
        }),
      },
      name: {
        show: true,
        required: false,
        access: computed(() => {
          return currentAdapter.value.state.capabilities.filters.role !== '' ||
            currentAdapter.value.state.capabilities.filters.namespace === ''
            ? 'read'
            : 'write';
        }),
      },
      role: {
        show: true,
        required: computed(() => {
          return currentAdapter.value.state.capabilities.filters.name !== '';
        }),
        access: computed(() => {
          return currentAdapter.value.state.capabilities.filters.name !== '' ? 'read' : 'write';
        }),
      },
    },
    actions: {
      getMany: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.capabilities.filters.role === '' ||
            currentAdapter.value.state.capabilities.filters.name !== ''
          );
        }),
      },
      getOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.capabilities.filters.role !== '' ||
            currentAdapter.value.state.capabilities.filters.app === '' ||
            currentAdapter.value.state.capabilities.filters.namespace === '' ||
            currentAdapter.value.state.capabilities.filters.name === ''
          );
        }),
      },
      postOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.capabilities.editForm.values.app === '' ||
            currentAdapter.value.state.capabilities.editForm.values.namespace === '' ||
            currentAdapter.value.state.capabilities.editForm.values.permissions.length === 0
          );
        }),
      },
      putOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.capabilities.editForm.values.app === '' ||
            currentAdapter.value.state.capabilities.editForm.values.namespace === '' ||
            currentAdapter.value.state.capabilities.editForm.values.name === '' ||
            currentAdapter.value.state.capabilities.editForm.values.permissions.length === 0
          );
        }),
      },
      deleteOne: {
        show: true,
        disabled: computed(() => {
          return (
            currentAdapter.value.state.capabilities.filters.app === '' ||
            currentAdapter.value.state.capabilities.filters.namespace === '' ||
            currentAdapter.value.state.capabilities.filters.name === ''
          );
        }),
      },
    },
    editForm: {
      app: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.capabilities.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      namespace: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.capabilities.editForm.mode === 'create' &&
            currentAdapter.value.state.capabilities.editForm.values.app !== ''
            ? 'write'
            : 'read';
        }),
      },
      name: {
        show: true,
        required: false,
        access: computed(() => {
          return currentAdapter.value.state.capabilities.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      displayName: {
        show: true,
        required: false,
        access: 'write',
      },
      role: {
        show: true,
        required: true,
        access: computed(() => {
          return currentAdapter.value.state.capabilities.editForm.mode === 'create' ? 'write' : 'read';
        }),
      },
      conditions: {
        show: true,
        required: false,
        access: 'write',
      },
      relation: {
        show: true,
        required: true,
        access: 'write',
      },
      permissions: {
        show: true,
        required: true,
        access: computed(() => {
          return permissions.value.length === 0 ||
            currentAdapter.value.state.capabilities.editForm.values.app === '' ||
            currentAdapter.value.state.capabilities.editForm.values.namespace === ''
            ? 'read'
            : 'write';
        }),
      },
    },
  },
});

// Adapters
const configuredAdapter: Adapter = {
  name: 'configured',
  adapter: new InMemoryDataAdapter(), // This will be swapped out during onMounted
  currentTab: 'apps',
  state: makeDefaultState(),
};
const inMemoryAdapter: Adapter = {
  name: 'inMemory',
  adapter: new InMemoryDataAdapter(),
  currentTab: 'apps',
  state: makeDefaultState(),
};
const apiAdapter: Adapter = {
  name: 'api',
  adapter: new ApiDataAdapter(
    new InMemoryAuthenticationAdapter('test-user', true),
    'http://localhost/guardian/management'
  ),
  currentTab: 'apps',
  state: makeDefaultState(),
};

const currentAdapter: Ref<Adapter> = ref(configuredAdapter);

// Form Data
const apps: Ref<DisplayApp[]> = ref([]);
const namespaces: Ref<DisplayNamespace[]> = ref([]);
const roles: Ref<DisplayRole[]> = ref([]);
const conditions: Ref<DisplayCondition[]> = ref([]);
const permissions: Ref<DisplayPermission[]> = ref([]);

// FilterForm Widgets
const rolesFilter: ComputedRef<Option[]> = computed(() => {
  if (!config.value[currentAdapter.value.currentTab].filters.role.show) {
    return [];
  }

  const roleOptions: Option[] = roles.value.map(role => {
    const roleId = `${role.appName}:${role.namespaceName}:${role.name}`;
    return {
      label: roleId,
      value: roleId,
    };
  });
  roleOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return roleOptions;
});
const appsFilter: ComputedRef<Option[]> = computed((): Option[] => {
  const filterOptions = config.value[currentAdapter.value.currentTab].filters;

  if (!filterOptions.app.show) {
    return [];
  }
  // When only showing apps as a filter, show all apps;
  // If we're showing namespaces too, then only show apps that have namespaces.
  if (!filterOptions.namespace.show) {
    return apps.value.map(app => {
      return {
        label: app.name,
        value: app.name,
      };
    });
  }

  const appOptions: Option[] = [];
  const seenValues: string[] = [];
  namespaces.value.forEach(ns => {
    if (seenValues.indexOf(ns.appName) !== -1) {
      return;
    }

    seenValues.push(ns.appName);
    appOptions.push({
      label: ns.appName,
      value: ns.appName,
    });
  });
  appOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return appOptions;
});
const namespacesFilter: ComputedRef<Option[]> = computed(() => {
  if (!config.value[currentAdapter.value.currentTab].filters.namespace.show) {
    return [];
  }

  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];

  const namespaceOptions: Option[] = [];
  namespaces.value.forEach(ns => {
    if (ns.appName === currentState.filters.app) {
      namespaceOptions.push({
        label: ns.name,
        value: ns.name,
      });
    }
  });
  namespaceOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return namespaceOptions;
});

// EditForm
const appsEditForm: ComputedRef<Option[]> = computed(() => {
  const editFormOptions = config.value[currentAdapter.value.currentTab].editForm;

  if (!editFormOptions?.app.show) {
    return [];
  }
  // When only showing apps as a filter, show all apps;
  // If we're showing namespaces too, then only show apps that have namespaces.
  if (!editFormOptions?.namespace.show) {
    return apps.value.map(app => {
      return {
        label: app.name,
        value: app.name,
      };
    });
  }

  const seenValues: string[] = [];
  const appOptions: Option[] = [];
  namespaces.value.forEach(ns => {
    if (seenValues.indexOf(ns.appName) !== -1) {
      return;
    }

    seenValues.push(ns.appName);
    appOptions.push({
      label: ns.appName,
      value: ns.appName,
    });
  });
  appOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return appOptions;
});
const namespacesEditForm: ComputedRef<Option[]> = computed(() => {
  if (!config.value[currentAdapter.value.currentTab].editForm?.namespace.show) {
    return [];
  }

  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];

  const namespaceOptions: Option[] = [];
  namespaces.value.forEach(ns => {
    if (ns.appName === currentState.editForm.values.app) {
      namespaceOptions.push({
        label: ns.name,
        value: ns.name,
      });
    }
  });
  namespaceOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return namespaceOptions;
});
const roleEditForm: ComputedRef<Option[]> = computed(() => {
  if (!config.value[currentAdapter.value.currentTab].filters.role.show) {
    return [];
  }

  const roleOptions: Option[] = roles.value.map(role => {
    const roleId = `${role.appName}:${role.namespaceName}:${role.name}`;
    return {
      label: roleId,
      value: roleId,
    };
  });
  roleOptions.sort((a, b) => {
    return a.value < b.value ? -1 : 1;
  });
  return roleOptions;
});
const conditionsEditFormProps: ComputedRef<SubElementProps[]> = computed(() => {
  const extensions: Record<string, any[]> = {};
  const options: Option[] = [];
  conditions.value.forEach(condition => {
    const conditionId = `${condition.appName}:${condition.namespaceName}:${condition.name}`;

    if (condition.parameters.length > 0) {
      const inputs: {type: any; props: any}[] = [];
      condition.parameters.forEach(param => {
        inputs.push({
          type: SubElement.UInputText,
          props: {
            label: `${param.name}`,
            name: `${conditionId}-${param.name}`,
            required: true,
          },
        });
      });
      extensions[conditionId] = inputs;
    }

    options.push({
      label: conditionId,
      value: `${conditionId}`,
    });
  });

  return [
    {
      type: SubElement.UExtendingInput,
      props: {
        name: 'condition-parameters',
        extensions: extensions,
        rootElement: {
          type: SubElement.UComboBox,
          props: {
            name: 'condition',
            label: 'Condition',
            options: options,
          },
        },
      },
    },
  ];
});
const permissionsEditFormProps: Ref<SubElementProps[]> = ref([
  {
    type: SubElement.UComboBox,
    props: {
      name: 'permission',
      label: 'Permission',
      options: computed(() => {
        const options: {label: string; value: string; disabled?: boolean | undefined}[] = [];
        permissions.value.forEach(perm => {
          options.push({
            label: `${perm.displayName}`,
            value: `${perm.appName}:${perm.namespaceName}:${perm.name}`,
          });
        });

        return options;
      }),
    },
  },
]);
const relationEditForm: Option[] = [
  {label: 'AND', value: 'AND'},
  {label: 'OR', value: 'OR'},
];

// Once we have an app and namespace for the editForm,
// we need to populate the permissions data for the form,
// if we need that data
const fetchPermissions = async () => {
  const currentTab = currentAdapter.value.currentTab;
  const currentState = currentAdapter.value.state[currentTab];

  currentState.error = '';

  if (!config.value[currentTab].editForm?.permissions.show) {
    return;
  }

  const editForm = currentAdapter.value.state[currentTab].editForm;
  const app = editForm.values.app;
  const namespace = editForm.values.namespace;

  editForm.values.permissions = [];
  if (app === '' || namespace === '') {
    return;
  }

  const permissionData = await currentAdapter.value.adapter.fetchPermissions(app, namespace);
  if (!permissionData.ok) {
    currentState.error = `Fetching permissions failed: ${permissionData.error}`;
    return;
  }
  permissions.value = permissionData.value.permissions;
};
const filterApp = computed(() => {
  return currentAdapter.value.state[currentAdapter.value.currentTab].filters.app;
});
const filterNamespace = computed(() => {
  return currentAdapter.value.state[currentAdapter.value.currentTab].filters.namespace;
});
const editFormApp = computed(() => {
  return currentAdapter.value.state[currentAdapter.value.currentTab].editForm.values.app;
});
const editFormNamespace = computed(() => {
  return currentAdapter.value.state[currentAdapter.value.currentTab].editForm.values.namespace;
});
watch(filterApp, () => {
  const currentFilters = currentAdapter.value.state[currentAdapter.value.currentTab].filters;
  currentFilters.namespace = '';
  currentFilters.name = '';
});
watch(filterNamespace, newNamespace => {
  if (newNamespace === '') {
    currentAdapter.value.state[currentAdapter.value.currentTab].filters.name = '';
  }
});
watch(editFormApp, async () => {
  await fetchPermissions();
});
watch(editFormNamespace, async () => {
  await fetchPermissions();
});

// This is how we reset the editForm data.
// Thanks, type-check, for making this so hacky.
const defaultEditFormValues: EditFormValues = {
  app: '',
  namespace: '',
  name: '',
  displayName: '',
  role: '',
  conditions: [],
  relation: 'AND',
  permissions: [],
};
const resetEditForm = () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];

  function updateEditForm<K extends keyof EditFormValues>(key: K) {
    currentState.editForm.values[key] = defaultEditFormValues[key];
  }

  let key: keyof EditFormValues;
  for (key in currentState.editForm.values) {
    updateEditForm(key);
  }
};

const switchToConfiguredAdapter = () => {
  currentAdapter.value = configuredAdapter;
};
const switchToInMemoryAdapter = () => {
  currentAdapter.value = inMemoryAdapter;
};
const switchToApiAdapter = () => {
  currentAdapter.value = apiAdapter;
};

const setupFormData = async () => {
  const currentConfig = config.value[currentAdapter.value.currentTab];
  currentAdapter.value.state[currentAdapter.value.currentTab].error = '';

  // For namespaces only, we want to get all apps.
  // For other tabs that use namespaces, we only show apps that have namespaces.
  if (currentAdapter.value.currentTab == 'namespaces') {
    const appData = await currentAdapter.value.adapter.fetchApps();
    if (!appData.ok) {
      currentAdapter.value.state[currentAdapter.value.currentTab].error = `Fetching apps failed: ${appData.error}`;
      return;
    }
    apps.value = appData.value.apps;
  }

  if (currentConfig.filters.namespace.show || currentConfig.editForm?.namespace.show) {
    const namespaceData = await currentAdapter.value.adapter.fetchNamespaces();
    if (!namespaceData.ok) {
      currentAdapter.value.state[currentAdapter.value.currentTab].error =
        `Fetching namespaces failed: ${namespaceData.error}`;
      return;
    }
    namespaces.value = namespaceData.value.namespaces ?? [];
  }

  if (currentConfig.filters.role.show) {
    const roleData = await currentAdapter.value.adapter.fetchRoles();
    if (!roleData.ok) {
      currentAdapter.value.state[currentAdapter.value.currentTab].error = `Fetching roles failed: ${roleData.error}`;
      return;
    }
    roles.value = roleData.value.roles ?? [];
  }

  if (currentConfig.editForm?.conditions.show) {
    const conditionData = await currentAdapter.value.adapter.fetchConditions();
    if (!conditionData.ok) {
      currentAdapter.value.state[currentAdapter.value.currentTab].error =
        `Fetching conditions failed: ${conditionData.error}`;
      return;
    }
    conditions.value = conditionData.value.conditions ?? [];
  }
};
const switchToApps = async () => {
  currentAdapter.value.currentTab = 'apps';
  await setupFormData();
};
const switchToNamespaces = async () => {
  currentAdapter.value.currentTab = 'namespaces';
  await setupFormData();
};
const switchToRoles = async () => {
  currentAdapter.value.currentTab = 'roles';
  await setupFormData();
};
const switchToContexts = async () => {
  currentAdapter.value.currentTab = 'contexts';
  await setupFormData();
};
const switchToPermissions = async () => {
  currentAdapter.value.currentTab = 'permissions';
  await setupFormData();
};
const switchToConditions = async () => {
  currentAdapter.value.currentTab = 'conditions';
  await setupFormData();
};
const switchToCapabilities = async () => {
  currentAdapter.value.currentTab = 'capabilities';
  await setupFormData();
};

const switchEditModeToCreate = () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  resetEditForm();
  currentState.editForm.mode = 'create';
};
const switchEditModeToUpdate = () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  if (currentState.all.length === 1) {
    const editObj: any = currentState.all[0];
    currentState.editForm.values.app = editObj.attributes.appName?.value ?? '';
    currentState.editForm.values.name = editObj.attributes.name?.value ?? '';
    currentState.editForm.values.displayName = editObj.attributes.displayName?.value ?? '';
    currentState.editForm.values.namespace = editObj.attributes.namespaceName?.value ?? '';
    currentState.editForm.values.role = editObj.attributes.role?.value ?? '';
    currentState.editForm.values.relation = editObj.attributes.relation?.value ?? '';

    const conditions: string[][] = [];
    const conditionData: string[] = editObj.attributes.conditions?.value ?? [];
    conditionData.forEach(conditionString => {
      const condStrings: string[] = [];
      const condition = JSON.parse(conditionString);
      const conditionId = `${condition.appName}:${condition.namespaceName}:${condition.name}`;
      const parameters: {name: string; value: string}[] = condition.parameters ?? [];
      parameters.sort((a, b) => {
        return a.name < b.name ? -1 : 1;
      });

      condStrings.push(conditionId);
      parameters.forEach(param => {
        condStrings.push(param.value);
      });
      conditions.push(condStrings);
    });
    currentState.editForm.values.conditions = conditions;

    const permissions: string[] = [];
    const permissionData = editObj.attributes.permissions?.value ?? [];
    permissionData.forEach((permString: any) => {
      const perm = JSON.parse(permString);
      permissions.push(`${perm.appName}:${perm.namespaceName}:${perm.name}`);
    });
    currentState.editForm.values.permissions = permissions;
  } else {
    resetEditForm();
  }

  currentState.editForm.mode = 'update';
};

const setListDisplay = (data: any[]) => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];

  const rows: UGridRow[] = [];
  const ids: string[] = [];
  data.forEach(obj => {
    const id = `${obj.appName ?? ''}${obj.appName ? ':' : ''}${obj.namespaceName ?? ''}${obj.namespaceName ? ':' : ''}${
      obj.name
    }`;
    const attributes: Record<string, Attribute> = {};
    for (const key in obj) {
      attributes[key] = {
        value: obj[key],
        access: 'read',
      };
    }

    rows.push({
      id: id,
      attributes: attributes,
    });
    ids.push(id);
  });
  currentState.all = rows;
  currentState.selection = ids;
};
const resetFilterForm = () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  currentState.filters.app = '';
  currentState.filters.namespace = '';
  currentState.filters.name = '';
  currentState.filters.role = '';
};
const resetListDisplay = () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  currentState.all = [];
  currentState.selection = [];
};

const formatConditions = (conditions?: DisplayCondition[]): any => {
  if (conditions === undefined) {
    return [];
  }

  const formattedConditions: any[] = [];
  conditions.forEach(condition => {
    condition.parameters.sort((a, b) => {
      return a.name < b.name ? -1 : 1;
    });

    const formattedCondition: any = {...condition};
    const parameters: string[] = [];
    condition.parameters.forEach((parameter: any) => {
      parameters.push(JSON.stringify(parameter));
    });

    formattedCondition.parameters = parameters;
    formattedConditions.push(formattedCondition);
  });

  return formattedConditions;
};

const formatCapability = (capability?: DisplayCapability): any => {
  if (capability === undefined) {
    return {};
  }

  const role = `${capability.role.appName}:${capability.role.namespaceName}:${capability.role.name}`;
  const formattedCapability: any = {...capability};
  const permissions: string[] = [];
  capability.permissions.forEach(permission => {
    permissions.push(JSON.stringify(permission));
  });
  const conditions: string[] = [];
  capability.conditions.forEach(condition => {
    conditions.push(JSON.stringify(condition));
  });

  formattedCapability.role = role;
  formattedCapability.permissions = permissions;
  formattedCapability.conditions = conditions;

  return formattedCapability;
};

const formatCapabilities = (capabilities?: DisplayCapability[]): any => {
  if (capabilities === undefined) {
    return [];
  }

  const formattedCapabilities: any[] = [];
  capabilities.forEach(capability => {
    formattedCapabilities.push(formatCapability(capability));
  });

  return formattedCapabilities;
};

const getMany = async () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  const adapter = currentAdapter.value.adapter;

  currentState.error = '';
  currentState.all = [];
  currentState.selection = [];

  function handleError(error: string): any[] {
    currentState.error = error;
    return [];
  }

  const data = await (async (): Promise<any[]> => {
    switch (currentAdapter.value.currentTab) {
      case 'apps': {
        const result = await adapter.fetchApps();
        if (!result.ok) {
          return handleError(result.error);
        }
        return result.value.apps;
      }
      case 'namespaces': {
        const result = await adapter.fetchNamespaces(currentState.filters.app);
        if (!result.ok) {
          return handleError(result.error);
        }
        return result.value.namespaces;
      }
      case 'roles': {
        const result = await adapter.fetchRoles(currentState.filters.app, currentState.filters.namespace);
        if (!result.ok) {
          return handleError(result.error);
        }
        return result.value.roles;
      }
      case 'contexts': {
        const result = await adapter.fetchContexts(currentState.filters.app, currentState.filters.namespace);
        if (!result.ok) {
          return handleError(result.error);
        }
        return result.value.contexts;
      }
      case 'permissions': {
        const result = await adapter.fetchPermissions(currentState.filters.app, currentState.filters.namespace);
        if (!result.ok) {
          return handleError(result.error);
        }
        return result.value.permissions;
      }
      case 'conditions': {
        const result = await adapter.fetchConditions();
        if (!result.ok) {
          return handleError(result.error);
        }
        return formatConditions(result.value.conditions);
      }
      case 'capabilities': {
        const role = currentState.filters.role.split(':');
        const result = await adapter.fetchCapabilities(
          {
            appName: role[0] ?? '',
            namespaceName: role[1] ?? '',
            name: role[2] ?? '',
          },
          currentState.filters.app,
          currentState.filters.namespace
        );
        if (!result.ok) {
          return handleError(result.error);
        }
        return formatCapabilities(result.value.capabilities);
      }
      default:
        return [];
    }
  })();

  setListDisplay(data);
  switchEditModeToCreate();
};

const getOne = async () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  const adapter = currentAdapter.value.adapter;

  currentState.error = '';
  currentState.all = [];
  currentState.selection = [];

  function handleError(error: FetchObjectError): any[] {
    currentState.error = (() => {
      switch (error.type) {
        case 'objectNotFound':
          return '404: Object does not exist';
        case 'generic':
          return error.message;
      }
    })();
    return [];
  }

  const data = await (async (): Promise<any[]> => {
    switch (currentAdapter.value.currentTab) {
      case 'namespaces': {
        const result = await adapter.fetchNamespace(currentState.filters.app, currentState.filters.name);
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.namespace];
      }
      case 'roles': {
        const result = await adapter.fetchRole(
          currentState.filters.app,
          currentState.filters.namespace,
          currentState.filters.name
        );
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.role];
      }
      case 'contexts': {
        const result = await adapter.fetchContext(
          currentState.filters.app,
          currentState.filters.namespace,
          currentState.filters.name
        );
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.context];
      }
      case 'capabilities': {
        const result = await adapter.fetchCapability(
          currentState.filters.app,
          currentState.filters.namespace,
          currentState.filters.name
        );
        if (!result.ok) {
          return handleError(result.error);
        }
        return [formatCapability(result.value.capability)];
      }
      default:
        return [];
    }
  })();

  setListDisplay(data);
  switchEditModeToUpdate();
};

const editOne = async () => {
  const currentState = currentAdapter.value.state[currentAdapter.value.currentTab];
  const adapter = currentAdapter.value.adapter;
  const formValues = currentState.editForm.values;
  const mode = currentState.editForm.mode;

  currentState.error = '';
  currentState.all = [];
  currentState.selection = [];

  function handleError(error: SaveError): any[] {
    switch (error.type) {
      case 'generic':
        currentState.error = error.message;
        break;
      case 'fieldErrors':
        currentState.error = 'Some fields are invalid. See in dev console';
        console.error(error);
        break;
    }
    return [];
  }
  const data = await (async (): Promise<any[]> => {
    switch (currentAdapter.value.currentTab) {
      case 'namespaces': {
        const editFunc =
          mode === 'update' ? adapter.updateNamespace.bind(adapter) : adapter.createNamespace.bind(adapter);
        const result = await editFunc({
          appName: formValues.app,
          name: formValues.name,
          displayName: formValues.displayName,
        });
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.namespace];
      }
      case 'roles': {
        const editFunc = mode === 'update' ? adapter.updateRole.bind(adapter) : adapter.createRole.bind(adapter);
        const result = await editFunc({
          appName: formValues.app,
          namespaceName: formValues.namespace,
          name: formValues.name,
          displayName: formValues.displayName,
        });
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.role];
      }
      case 'contexts': {
        const editFunc = mode === 'update' ? adapter.updateContext.bind(adapter) : adapter.createContext.bind(adapter);
        const result = await editFunc({
          appName: formValues.app,
          namespaceName: formValues.namespace,
          name: formValues.name,
          displayName: formValues.displayName,
        });
        if (!result.ok) {
          return handleError(result.error);
        }
        return [result.value.context];
      }
      case 'capabilities': {
        const editFunc =
          mode === 'update' ? adapter.updateCapability.bind(adapter) : adapter.createCapability.bind(adapter);

        const outgoingRole = formValues.role.split(':');
        const outgoingConditions: any[] = [];
        const outgoingPermissions: any[] = [];
        formValues.conditions.forEach(conditionData => {
          const conditionId = conditionData[0];
          if (!conditionId) return;
          const conditionParts = conditionId.split(':');
          const condition = conditions.value.filter(cond => {
            return (
              cond.appName === conditionParts[0] &&
              cond.namespaceName === conditionParts[1] &&
              cond.name === conditionParts[2]
            );
          })[0];
          if (!condition) return;
          const parameters: any[] = [];
          for (let i = 1; i < conditionData.length; i++) {
            const param = condition.parameters[i - 1];
            if (param) {
              parameters.push({
                name: param.name,
                value: conditionData[i],
              });
            }
          }
          outgoingConditions.push({
            appName: condition.appName,
            namespaceName: condition.namespaceName,
            name: condition.name,
            parameters: parameters,
          });
        });
        formValues.permissions.forEach(permData => {
          const permissionParts = permData.split(':');
          outgoingPermissions.push({
            appName: permissionParts[0] ?? '',
            namespaceName: permissionParts[1] ?? '',
            name: permissionParts[2] ?? '',
          });
        });
        const result = await editFunc({
          appName: formValues.app,
          namespaceName: formValues.namespace,
          name: formValues.name,
          displayName: formValues.displayName,
          role: {
            appName: outgoingRole[0] ?? '',
            namespaceName: outgoingRole[1] ?? '',
            name: outgoingRole[2] ?? '',
          },
          conditions: outgoingConditions,
          relation: formValues.relation,
          permissions: outgoingPermissions,
        });
        if (!result.ok) {
          return handleError(result.error);
        }
        return [formatCapability(result.value.capability)];
      }
      default:
        return [];
    }
  })();

  setListDisplay(data);
  switchEditModeToUpdate();
};

const deleteOne = async () => {
  const currentTab = currentAdapter.value.currentTab;
  const currentState = currentAdapter.value.state[currentTab];

  if (currentTab !== 'capabilities') {
    return;
  }

  currentState.error = '';

  const result = await currentAdapter.value.adapter.removeCapability(
    currentState.filters.app,
    currentState.filters.namespace,
    currentState.filters.name
  );
  if (!result.ok) {
    currentState.error = result.error;
  }

  resetListDisplay();
  switchEditModeToCreate();
};

onMounted(async () => {
  await settingsStore.init();
  const adapterStore = useAdapterStore(settingsStore.config);
  configuredAdapter.adapter = adapterStore.dataAdapter;

  loading.value = false;
});
</script>

<template>
  <template></template>
  <main
    v-if="!loading"
    class="testView"
  >
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>

    <h2>Data Adapter Tests</h2>

    <div class="testButtonsWrapper">
      <UButton
        :class="{'uButton--flat': currentAdapter.name !== 'configured'}"
        type="button"
        label="Configured Global Adapter"
        @click="switchToConfiguredAdapter"
      />
      <UButton
        :class="{'uButton--flat': currentAdapter.name !== 'inMemory'}"
        type="button"
        label="In Memory Adapter"
        @click="switchToInMemoryAdapter"
      />
      <UButton
        :class="{'uButton--flat': currentAdapter.name !== 'api'}"
        type="button"
        label="API Adapter"
        @click="switchToApiAdapter"
      />
    </div>
    <p v-show="currentAdapter.name === 'configured'">Test the adapter configured in the .env file</p>
    <p v-show="currentAdapter.name === 'inMemory'">Test the in-memory adapter</p>
    <p v-show="currentAdapter.name === 'api'">
      Test an adapter running against the Management API, without authentication. You have to set
      GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT=fast_api_always_authorized for this to work.
    </p>

    <div class="testWrapper">
      <div class="uContainer uCard listDisplay">
        <div class="testButtonsWrapper">
          <UButton
            v-show="config[currentAdapter.currentTab].filters.app.show"
            type="button"
            label="Reset Form"
            @click="resetFilterForm"
          />
        </div>

        <div class="testButtonsWrapper">
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'apps'}"
            type="button"
            label="Apps"
            @click="switchToApps"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'namespaces'}"
            type="button"
            label="Namespaces"
            @click="switchToNamespaces"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'roles'}"
            type="button"
            label="Roles"
            @click="switchToRoles"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'contexts'}"
            type="button"
            label="Contexts"
            @click="switchToContexts"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'permissions'}"
            type="button"
            label="Permissions"
            @click="switchToPermissions"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'conditions'}"
            type="button"
            label="Conditions"
            @click="switchToConditions"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.currentTab !== 'capabilities'}"
            type="button"
            label="Capabilities"
            @click="switchToCapabilities"
          />
        </div>

        <UComboBox
          v-show="config[currentAdapter.currentTab].filters.role.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].filters.role"
          name="role-filter"
          label="Filter by Role (app:namespace:rolename)"
          description="Role to use to filter objects"
          :required="config[currentAdapter.currentTab].filters.role.required"
          :access="config[currentAdapter.currentTab].filters.role.access"
          :options="rolesFilter"
        />
        <UComboBox
          v-show="config[currentAdapter.currentTab].filters.app.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].filters.app"
          name="app-filter"
          label="Filter by App"
          description="App name to use to filter objects"
          :required="config[currentAdapter.currentTab].filters.app.required"
          :access="config[currentAdapter.currentTab].filters.app.access"
          :options="appsFilter"
        />
        <UComboBox
          v-show="config[currentAdapter.currentTab].filters.namespace.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].filters.namespace"
          name="namespace-filter"
          label="Filter by Namespace (requires App)"
          description="Namespace name to use to filter objects"
          :required="config[currentAdapter.currentTab].filters.namespace.required"
          :access="config[currentAdapter.currentTab].filters.namespace.access"
          :options="namespacesFilter"
        />
        <UInputText
          v-show="config[currentAdapter.currentTab].filters.name.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].filters.name"
          name="name-filter"
          label="Filter by Name (requires App and Namespace)"
          description="Name to use to filter objects"
          :required="config[currentAdapter.currentTab].filters.name.required"
          :access="config[currentAdapter.currentTab].filters.name.access"
        />

        <div class="testButtonsWrapper subtestButtonsWrapper">
          <UButton
            v-show="config[currentAdapter.currentTab].actions.getMany.show"
            type="button"
            label="GET Many"
            :disabled="config[currentAdapter.currentTab].actions.getMany.disabled"
            @click="getMany"
          />
          <UButton
            v-show="config[currentAdapter.currentTab].actions.getOne.show"
            type="button"
            label="GET One"
            :disabled="config[currentAdapter.currentTab].actions.getOne.disabled"
            @click="getOne"
          />
          <UButton
            v-show="config[currentAdapter.currentTab].actions.deleteOne.show"
            type="button"
            label="DELETE One"
            :disabled="config[currentAdapter.currentTab].actions.deleteOne.disabled"
            @click="deleteOne"
          />
        </div>

        <p class="error">{{ currentAdapter.state[currentAdapter.currentTab].error }}</p>

        <UGrid
          v-model:selection="currentAdapter.state[currentAdapter.currentTab].selection"
          class="testView__uGrid"
          :rows="currentAdapter.state[currentAdapter.currentTab].all"
          :columns="config[currentAdapter.currentTab].columns"
          :globalActions="[]"
          :contextActions="[]"
          :itemsPerPageOptions="[20, 50, -1]"
        />
      </div>
      <div
        v-if="config[currentAdapter.currentTab].editForm !== null"
        class="uContainer uCard dataDisplay"
      >
        <h3>
          {{ currentAdapter.state[currentAdapter.currentTab].editForm.mode.charAt(0).toUpperCase()
          }}{{ currentAdapter.state[currentAdapter.currentTab].editForm.mode.slice(1) }} {{ currentAdapter.currentTab }}
        </h3>

        <div class="testButtonsWrapper subtestButtonsWrapper">
          <UButton
            :class="{'uButton--flat': currentAdapter.state[currentAdapter.currentTab].editForm.mode !== 'create'}"
            type="button"
            label="Create"
            @click="switchEditModeToCreate"
          />
          <UButton
            :class="{'uButton--flat': currentAdapter.state[currentAdapter.currentTab].editForm.mode !== 'update'}"
            type="button"
            label="Update"
            @click="switchEditModeToUpdate"
          />
        </div>

        <p
          class="error"
          v-show="
            currentAdapter.state[currentAdapter.currentTab].editForm.mode === 'update' &&
            currentAdapter.currentTab === 'capabilities'
          "
        >
          WARNING: The univention-veb widgets may not load all data the first time this form is populated. Click
          "UPDATE" again to reload all data.
        </p>

        <p v-show="currentAdapter.state[currentAdapter.currentTab].editForm.mode === 'update'">
          HINT: Use "GET ONE" to find a specific object to populate this form.
        </p>

        <UComboBox
          v-show="config[currentAdapter.currentTab].editForm?.role.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.role"
          name="editForm-role"
          label="Role"
          :required="config[currentAdapter.currentTab].editForm?.role.required"
          :access="config[currentAdapter.currentTab].editForm?.role.access ?? 'read'"
          :options="roleEditForm"
        />
        <UComboBox
          v-show="config[currentAdapter.currentTab].editForm?.app.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.app"
          name="editForm-app"
          label="App Name"
          description="Name of the app that this object belongs to"
          :required="config[currentAdapter.currentTab].editForm?.app.required"
          :access="config[currentAdapter.currentTab].editForm?.app.access ?? 'read'"
          :options="appsEditForm"
        />
        <UComboBox
          v-show="config[currentAdapter.currentTab].editForm?.namespace.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.namespace"
          name="editForm-namespace"
          label="Namespace Name"
          description="Name of the namespace that this object belongs to"
          :required="config[currentAdapter.currentTab].editForm?.namespace.required"
          :access="config[currentAdapter.currentTab].editForm?.namespace.access ?? 'read'"
          :options="namespacesEditForm"
        />
        <UInputText
          v-show="config[currentAdapter.currentTab].editForm?.name.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.name"
          name="editForm-name"
          label="Name"
          description="Name of the object"
          :required="config[currentAdapter.currentTab].editForm?.name.required"
          :access="config[currentAdapter.currentTab].editForm?.name.access ?? 'read'"
        />
        <UInputText
          v-show="config[currentAdapter.currentTab].editForm?.displayName.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.displayName"
          name="editForm-displayName"
          label="Display Name"
          description="Display name of the object"
          :required="config[currentAdapter.currentTab].editForm?.displayName.required"
          :access="config[currentAdapter.currentTab].editForm?.displayName.access ?? 'read'"
        />
        <UMultiInput
          v-show="config[currentAdapter.currentTab].editForm?.conditions.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.conditions"
          name="editForm-conditions"
          label="Conditions"
          :required="config[currentAdapter.currentTab].editForm?.conditions.required"
          :subElements="conditionsEditFormProps"
          :access="config[currentAdapter.currentTab].editForm?.conditions.access ?? 'read'"
        />
        <UComboBox
          v-show="config[currentAdapter.currentTab].editForm?.relation.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.relation"
          name="editForm-relation"
          label="Relation"
          :required="config[currentAdapter.currentTab].editForm?.relation.required"
          :options="relationEditForm"
          :access="config[currentAdapter.currentTab].editForm?.relation.access ?? 'read'"
        />
        <UMultiInput
          v-show="config[currentAdapter.currentTab].editForm?.permissions.show"
          v-model="currentAdapter.state[currentAdapter.currentTab].editForm.values.permissions"
          name="editForm-permissions"
          label="Permissions"
          :required="config[currentAdapter.currentTab].editForm?.permissions.required"
          :access="config[currentAdapter.currentTab].editForm?.permissions.access ?? 'read'"
          :subElements="permissionsEditFormProps"
        />

        <UButton
          v-show="currentAdapter.state[currentAdapter.currentTab].editForm.mode === 'create'"
          type="button"
          label="POST One"
          :disabled="config[currentAdapter.currentTab].actions.postOne.disabled"
          @click="editOne"
        />
        <UButton
          v-show="currentAdapter.state[currentAdapter.currentTab].editForm.mode === 'update'"
          type="button"
          label="PUT One"
          :disabled="config[currentAdapter.currentTab].actions.putOne.disabled"
          @click="editOne"
        />
      </div>
    </div>
  </main>
</template>

<style lang="stylus">
main.testView
  .listDisplay
    width: 65%
  .dataDisplay
    width: 35%
</style>
