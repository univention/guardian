<script setup lang="ts">
import type {UGridContextAction, UGridRow} from '@univention/univention-veb';
import {
  UButton,
  UComboBox,
  UConfirmDialog,
  UExtendingInput,
  UGrid,
  type UGridColumnDefinition,
  UInputCheckbox,
  UInputClassified,
  UInputDate,
  UInputPassword,
  UInputText,
  UMultiInput,
  UMultiObjectSelect,
  UMultiSelect,
  USelect,
  useStandby,
  UStandbyFullScreen,
} from '@univention/univention-veb';
import type {Field, FieldComboBox, FormValues, GlobalAction, ListResponseModel, ObjectType} from '@/helpers/models';
import {useRoute, useRouter} from 'vue-router';
import {deleteCapabilities, fetchListViewConfig, fetchNamespacesOptions, fetchObjects} from '@/helpers/dataAccess';
import {computed, type ComputedRef, onMounted, reactive, ref, toRaw, watch} from 'vue';
import {useTranslation} from 'i18next-vue';
import {useErrorStore} from '@/stores/error';

const props = defineProps<{
  objectType: ObjectType;
}>();

const components = {
  UComboBox,
  UExtendingInput,
  UInputCheckbox,
  UInputDate,
  UInputPassword,
  UInputText,
  UMultiInput,
  UMultiObjectSelect,
  UMultiSelect,
  USelect,
  UInputClassified,
};

interface GridRow extends UGridRow {
  allowedActions: string[];
}

const {t} = useTranslation();
const router = useRouter();

const loading = ref(true);
const standby = reactive(useStandby());

interface Config {
  allowedGlobalActions: GlobalAction[];
  searchForm: Field[];
  searchFormOrigValues: FormValues;
  columns: UGridColumnDefinition[];
}
interface Configs {
  role: Config;
  context: Config;
  namespace: Config;
  capability: Config;
}
const configs = ref<Configs>({
  role: {
    allowedGlobalActions: [],
    searchForm: [],
    searchFormOrigValues: {},
    columns: [],
  },
  context: {
    allowedGlobalActions: [],
    searchForm: [],
    searchFormOrigValues: {},
    columns: [],
  },
  namespace: {
    allowedGlobalActions: [],
    searchForm: [],
    searchFormOrigValues: {},
    columns: [],
  },
  capability: {
    allowedGlobalActions: [],
    searchForm: [],
    searchFormOrigValues: {},
    columns: [],
  },
});
const config = computed(() => configs.value[props.objectType]);
const errorStore = useErrorStore();

const fetchConfig = async (): Promise<void> => {
  const result = await fetchListViewConfig();
  if (!result.ok) {
    errorStore.push({
      title: t('ErrorModal.heading'),
      message: t('ListView.fetchConfig.error', {msg: result.error}),
      unRecoverable: true,
    });
    return;
  }
  const listViewConfig = result.value;

  configs.value.role.allowedGlobalActions = listViewConfig.role.allowedGlobalActions;
  configs.value.role.searchForm = listViewConfig.role.searchForm;
  configs.value.role.searchFormOrigValues = structuredClone(listViewConfig.role.searchFormValues);
  configs.value.role.columns = listViewConfig.role.columns;

  configs.value.context.allowedGlobalActions = listViewConfig.context.allowedGlobalActions;
  configs.value.context.searchForm = listViewConfig.context.searchForm;
  configs.value.context.searchFormOrigValues = structuredClone(listViewConfig.context.searchFormValues);
  configs.value.context.columns = listViewConfig.context.columns;

  configs.value.namespace.allowedGlobalActions = listViewConfig.namespace.allowedGlobalActions;
  configs.value.namespace.searchForm = listViewConfig.namespace.searchForm;
  configs.value.namespace.searchFormOrigValues = structuredClone(listViewConfig.namespace.searchFormValues);
  configs.value.namespace.columns = listViewConfig.namespace.columns;

  configs.value.capability.allowedGlobalActions = listViewConfig.capability.allowedGlobalActions;
  configs.value.capability.searchForm = listViewConfig.capability.searchForm;
  configs.value.capability.searchFormOrigValues = structuredClone(listViewConfig.capability.searchFormValues);
  configs.value.capability.columns = listViewConfig.capability.columns;

  // setup watching of 'appSelection' field to fill 'namespaceSelection'
  const listViewsToWatchNamespace = [
    {
      config: configs.value.role,
      state: states.value.role,
    },
    {
      config: configs.value.context,
      state: states.value.context,
    },
    {
      config: configs.value.capability,
      state: states.value.capability,
    },
  ];
  for (const o of listViewsToWatchNamespace) {
    const field = o.config.searchForm.find(f => f.props.name === 'namespaceSelection') as FieldComboBox;
    const _standby = reactive(useStandby());
    field.props.standby = computed(() => _standby.active);

    watch(
      () => o.state.searchFormValues['appSelection'],
      async newValue => {
        if (newValue === '') {
          field.props.access = 'read';
          field.props.options = [
            {
              label: t('dataAccess.options.all'),
              value: '',
            },
          ];
          o.state.searchFormValues['namespaceSelection'] = '';
        } else {
          field.props.access = 'write';
          o.state.searchFormValues['namespaceSelection'] = '';
          const result = await _standby.wrap(() => fetchNamespacesOptions(newValue as string, true));
          if (!result.ok) {
            errorStore.push({
              title: t('ErrorModal.heading'),
              message: t('ListView.fetchNamespacesOptions.error', {app: newValue, msg: result.error}),
            });
            field.props.options = [
              {
                label: t('dataAccess.options.all'),
                value: '',
              },
            ];
          } else {
            field.props.options = result.value;
          }
          o.state.searchFormValues['namespaceSelection'] = '';
        }
      }
    );
  }

  states.value.role.searchFormValues = structuredClone(listViewConfig.role.searchFormValues);
  states.value.context.searchFormValues = structuredClone(listViewConfig.context.searchFormValues);
  states.value.namespace.searchFormValues = structuredClone(listViewConfig.namespace.searchFormValues);
  states.value.capability.searchFormValues = structuredClone(listViewConfig.capability.searchFormValues);
};

onMounted(async () => {
  await standby.wrap(() => fetchConfig());
  loading.value = false;
});

interface State {
  searchFormValues: FormValues;
  selection: string[];
  rows: ListResponseModel[];
}
interface States {
  role: State;
  context: State;
  namespace: State;
  capability: State;
}
const states = ref<States>({
  role: {
    searchFormValues: {},
    selection: [],
    rows: [],
  },
  context: {
    searchFormValues: {},
    selection: [],
    rows: [],
  },
  namespace: {
    searchFormValues: {},
    selection: [],
    rows: [],
  },
  capability: {
    searchFormValues: {},
    selection: [],
    rows: [],
  },
});
const state = computed(() => states.value[props.objectType]);

const searchLimitReachedModalActive = ref(false);
const search = async (keepSelection = false): Promise<void> => {
  const result = await standby.wrap(() =>
    fetchObjects(props.objectType, state.value.searchFormValues, route.params.id as string)
  );
  if (!result.ok) {
    errorStore.push({
      title: t('ErrorModal.heading'),
      message: t('ListView.fetchObjects.error', {msg: result.error}),
    });
    return;
  }
  if (result.value) {
    states.value[props.objectType].rows = result.value;
  }
  if (keepSelection) {
    const rowIds = new Set(state.value.rows.map(row => row.id));
    states.value[props.objectType].selection = state.value.selection.filter(selectionId => rowIds.has(selectionId));
  } else {
    states.value[props.objectType].selection = [];
  }
};

const reset = (): void => {
  states.value[props.objectType].searchFormValues = structuredClone(toRaw(config.value.searchFormOrigValues));
};

const route = useRoute();
watch(
  () => route.query['refetch'],
  async val => {
    if (val !== undefined) {
      const query = JSON.parse(JSON.stringify(route.query));
      delete query.refetch;
      router.replace({
        ...route,
        query,
      });
      if (state.value.rows.length > 0) {
        await search(true);
      }
    }
  },
  {
    immediate: true,
  }
);

const onAddAction = (): void => {
  const name = {
    role: 'addRole',
    context: 'addContext',
    namespace: 'addNamespace',
    capability: 'addCapability',
  }[props.objectType];
  router.push({
    name,
  });
};

const deleteModalError = reactive({
  active: false,
  failedCapabilities: [] as {id: string; error: string}[],
});
const deleteModalActive = ref(false);
const deleteModalProps = reactive<{
  selected: string[];
  toDelete: string[];
}>({
  selected: [],
  toDelete: [],
});
const onDelete = async (ids: string[]): Promise<void> => {
  deleteModalActive.value = false;
  const failedCapabilities = await standby.wrap(() => deleteCapabilities(ids));
  console.log(failedCapabilities);
  if (failedCapabilities.length) {
    deleteModalError.failedCapabilities = failedCapabilities;
    deleteModalError.active = true;
  }

  // remove successfully deleted objects from list and selection
  const failedIdsSet = new Set(failedCapabilities.map(x => x.id));
  const successes = new Set(ids.filter(id => !failedIdsSet.has(id)));
  states.value.capability.rows = states.value.capability.rows.filter(row => !successes.has(row.id));
  states.value.capability.selection = states.value.capability.selection.filter(id => !successes.has(id));
};

const canDo =
  (action: string): ((row: UGridRow) => boolean) =>
  (row: UGridRow) =>
    (row as GridRow).allowedActions.includes(action);
const editContextAction: ComputedRef<UGridContextAction> = computed(() => ({
  label: t('ListView.contextActions.editLabel'),
  icon: 'edit-2',
  callback: (ids: string[]): void => {
    // TODO sanitize ids
    const name = {
      role: 'editRole',
      context: 'editContext',
      namespace: 'editNamespace',
      capability: 'editCapability',
    }[props.objectType];
    if (props.objectType === 'capability') {
      router.push({
        name,
        params: {
          id2: ids[0],
        },
      });
    } else {
      router.push({
        name,
        params: {
          id: ids[0],
        },
      });
    }
  },
  canExecute: canDo('edit'),
  multi: false,
}));
const contextActions: ComputedRef<UGridContextAction[]> = computed(() => {
  const actions = [editContextAction.value];
  if (props.objectType === 'capability') {
    actions.push({
      label: t('ListView.contextActions.deleteLabel'),
      icon: 'trash',
      callback: (ids: string[], objectsToDelete: UGridRow[], sel: string[]): void => {
        deleteModalProps.selected = sel;
        deleteModalProps.toDelete = ids;
        deleteModalActive.value = true;
      },
      canExecute: canDo('delete'),
      multi: true,
      enablingMode: 'some',
    });
  }
  return actions;
});

const globalActions = computed(() => {
  return [
    {
      label: t('ListView.globalActions.addLabel'),
      icon: 'plus',
      callback: onAddAction,
      disabled: !config.value.allowedGlobalActions.includes('add'),
    },
  ];
});

const heading = computed(() => {
  function lastIdPart(id: string): string {
    const split = id.split(':');
    return split[split.length - 1];
  }
  if (props.objectType === 'capability') {
    return `${t(`EditView.heading.edit.role`)} > ${lastIdPart(route.params['id'] as string)} > ${t(
      'ListView.heading.capability'
    )}`;
  }

  return t(`ListView.heading.${props.objectType}`);
});
</script>

<template>
  <main v-if="!loading" class="listView">
    <div class="listView__header" :class="`listView__header--${props.objectType}`">
      <h1 class="listView__header__heading">
        {{ heading }}
      </h1>
      <div v-if="props.objectType === 'capability'" class="listView__header__buttons">
        <RouterLink class="uButton routerButton" :to="{name: 'editRole', query: {back: 'true'}}">
          {{ t('EditView.button.back') }}
        </RouterLink>
      </div>
    </div>
    <div class="routeButtonsWrapper">
      <div class="routeButtons">
        <template v-if="props.objectType === 'capability'">
          <RouterLink class="uButton uButton--flat" :to="{name: 'editRole'}">
            {{ t('EditView.headerLink.editRole') }}
          </RouterLink>
          <RouterLink class="uButton" :to="{name: 'listCapabilities'}">
            {{ t('EditView.headerLink.listCapabilities') }}
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink class="uButton" :class="{'uButton--flat': props.objectType !== 'role'}" :to="{name: 'listRoles'}">
            {{ t('ListView.heading.role') }}
          </RouterLink>
          <RouterLink
            class="uButton"
            :class="{'uButton--flat': props.objectType !== 'namespace'}"
            :to="{name: 'listNamespaces'}"
          >
            {{ t('ListView.heading.namespace') }}
          </RouterLink>
          <RouterLink
            class="uButton"
            :class="{'uButton--flat': props.objectType !== 'context'}"
            :to="{name: 'listContexts'}"
          >
            {{ t('ListView.heading.context') }}
          </RouterLink>
        </template>
      </div>
    </div>
    <form @submit.prevent="search(false)">
      <div class="searchForm__elements">
        <component
          :is="components[field.type]"
          v-for="field in config.searchForm"
          :key="field.props.name"
          v-bind="field.props"
          v-model:modelValue="state.searchFormValues[field.props.name]"
        />
      </div>
      <div class="searchForm__buttons">
        <UButton type="button" :label="t('ListView.searchForm.resetButtonLabel')" @click="reset" />
        <UButton primary type="submit" icon="search" :label="t('ListView.searchForm.searchButtonLabel')" />
      </div>
    </form>
    <template v-if="props.objectType === 'capability'">
      <UGrid
        v-model:selection="states.capability.selection"
        class="listView__uGrid"
        :columns="configs.capability.columns"
        :globalActions="globalActions"
        :contextActions="contextActions"
        :rows="states.capability.rows"
        :itemsPerPageOptions="[20, 50, -1]"
        :clickCallback="editContextAction"
      />
    </template>
    <template v-else>
      <UGrid
        v-show="objectType === 'role'"
        v-model:selection="states.role.selection"
        class="listView__uGrid"
        :columns="configs.role.columns"
        :globalActions="globalActions"
        :contextActions="contextActions"
        :rows="states.role.rows"
        :itemsPerPageOptions="[20, 50, -1]"
        :clickCallback="editContextAction"
      />
      <UGrid
        v-show="objectType === 'context'"
        v-model:selection="states.context.selection"
        class="listView__uGrid"
        :columns="configs.context.columns"
        :globalActions="globalActions"
        :contextActions="contextActions"
        :rows="states.context.rows"
        :itemsPerPageOptions="[20, 50, -1]"
        :clickCallback="editContextAction"
      />
      <UGrid
        v-show="objectType === 'namespace'"
        v-model:selection="states.namespace.selection"
        class="listView__uGrid"
        :columns="configs.namespace.columns"
        :globalActions="globalActions"
        :contextActions="contextActions"
        :rows="states.namespace.rows"
        :itemsPerPageOptions="[20, 50, -1]"
        :clickCallback="editContextAction"
      />
    </template>
    <UConfirmDialog
      v-model:active="deleteModalActive"
      :title="t('DeleteModal.title')"
      :confirmLabel="t('DeleteModal.confirmLabel')"
      :cancelLabel="t('DeleteModal.cancelLabel')"
      @confirm="onDelete(deleteModalProps.toDelete)"
    >
      <template #description>
        <div>
          <p>
            {{
              t('DeleteModal.description', {
                toDelete: deleteModalProps.toDelete.length,
                selected: deleteModalProps.selected.length,
              })
            }}
          </p>
          <p v-if="deleteModalProps.toDelete.length !== deleteModalProps.selected.length">
            {{
              t('DeleteModal.warning', {
                numberWarning: deleteModalProps.selected.length - deleteModalProps.toDelete.length,
                selected: deleteModalProps.selected.length,
              })
            }}
          </p>
        </div>
      </template>
    </UConfirmDialog>
    <UConfirmDialog
      v-model:active="deleteModalError.active"
      :title="t('DeleteModalError.title')"
      :confirmLabel="t('DeleteModalError.confirmLabel')"
      hideCancel
    >
      <template #description>
        <div>
          <p>
            {{ t('DeleteModalError.description') }}
          </p>
          <ul>
            <li v-for="fail in deleteModalError.failedCapabilities" :key="fail.id">{{ fail.id }} - {{ fail.error }}</li>
          </ul>
        </div>
      </template>
    </UConfirmDialog>
    <UConfirmDialog
      v-model:active="searchLimitReachedModalActive"
      :title="t('SearchLimitReachedModal.title')"
      :confirmLabel="t('SearchLimitReachedModal.button.confirm')"
      @confirm="search(false)"
    >
      <template #description>
        <p>
          {{ t('SearchLimitReachedModal.description', {limit: 2000}) }}
        </p>
      </template>
    </UConfirmDialog>
  </main>
  <UStandbyFullScreen :active="standby.active" />
</template>

<style lang="stylus">
main.listView
  padding: calc(4 * var(--layout-spacing-unit))
  margin: 0 auto
  height: 100vh
  display: flex
  flex-direction: column
  max-width: 1140px

  h1
    margin: 0

  .searchForm__elements
    display: flex
    gap: var(--layout-spacing-unit) calc(2 * var(--layout-spacing-unit))

    .uFormElement
      flex: 1 1 auto

  .searchForm__buttons
    display: flex
    justify-content: flex-end
    grid-gap: calc(2 * var(--layout-spacing-unit))

  .listView__uGrid
    margin-top: calc(4 * var(--layout-spacing-unit))

  .routeButtonsWrapper
    display: flex
    margin: calc(2 * var(--layout-spacing-unit)) 0

.routerButton
  text-decoration: none
.routeButtons
  display: flex
  border: 1px solid var(--font-color-contrast-low)
  border-radius: var(--button-border-radius)
  overflow: hidden

  > .uButton
    @extends .routerButton
    padding: 0 calc(2 * var(--layout-spacing-unit))
    border-radius: 0
</style>
