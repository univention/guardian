<script setup lang="ts">
import {
  UGrid,
  UInputText,
  UButton,
  UComboBox,
  UStandbyFullScreen,
  useStandby,
  UConfirmDialog,
  UInputPassword,
  UInputCheckbox,
  UInputDate,
  UMultiInput,
  UMultiObjectSelect,
  UMultiSelect,
  USelect,
  UInputClassified,
  type UGridColumnDefinition,
} from '@univention/univention-veb';
import type {UGridContextAction, UGridRow} from '@univention/univention-veb';
import type {ListResponseModel, GlobalAction, Field, FormValues, ObjectType} from '@/helpers/models';
import {useRoute} from 'vue-router';
import {fetchListViewConfig, fetchNamespaces, fetchObjects} from '@/helpers/dataAccess';
import {ref, onMounted, watch, reactive, toRaw, computed, type ComputedRef} from 'vue';
import {useTranslation} from 'i18next-vue';
import {useRouter} from 'vue-router';
import {config as appConfig} from '@/helpers/config';
import type {FieldComboBox} from '@/helpers/models';

const props = defineProps<{
  objectType: ObjectType;
}>();

const components = {
  UComboBox,
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
});
const config = computed(() => configs.value[props.objectType]);

const fetchConfig = async (): Promise<void> => {
  const listViewConfig = await fetchListViewConfig();

  configs.value.role.allowedGlobalActions = listViewConfig.role.allowedGlobalActions;
  configs.value.role.searchForm = listViewConfig.role.searchForm;
  configs.value.role.searchFormOrigValues = structuredClone(listViewConfig.role.searchFormValues);
  configs.value.role.columns = listViewConfig.role.columns;
  {
    const field = configs.value.role.searchForm.find(f => f.props.name === 'namespaceSelection') as FieldComboBox;
    const _standby = reactive(useStandby());
    field.props.standby = computed(() => _standby.active);

    watch(
      () => states.value.role.searchFormValues['appSelection'],
      async newValue => {
        if (newValue === 'all') {
          field.props.access = 'read';
          field.props.options = [
            {
              label: 'All',
              value: 'all',
            },
          ];
          states.value.role.searchFormValues['namespaceSelection'] = 'all';
        } else {
          field.props.access = 'write';
          states.value.role.searchFormValues['namespaceSelection'] = '';
          const _options = await _standby.wrap(() => fetchNamespaces(newValue as string));
          _options.unshift({
            label: 'All',
            value: 'all',
          });
          field.props.options = _options;
          states.value.role.searchFormValues['namespaceSelection'] = 'all';
        }
      }
    );
  }

  configs.value.context.allowedGlobalActions = listViewConfig.context.allowedGlobalActions;
  configs.value.context.searchForm = listViewConfig.context.searchForm;
  configs.value.context.searchFormOrigValues = structuredClone(listViewConfig.context.searchFormValues);
  configs.value.context.columns = listViewConfig.context.columns;
  {
    const field = configs.value.context.searchForm.find(f => f.props.name === 'namespaceSelection') as FieldComboBox;
    const _standby = reactive(useStandby());
    field.props.standby = computed(() => _standby.active);

    watch(
      () => states.value.context.searchFormValues['appSelection'],
      async newValue => {
        if (newValue === 'all') {
          field.props.access = 'read';
          field.props.options = [
            {
              label: 'All',
              value: 'all',
            },
          ];
          states.value.context.searchFormValues['namespaceSelection'] = 'all';
        } else {
          field.props.access = 'write';
          states.value.context.searchFormValues['namespaceSelection'] = '';
          const _options = await _standby.wrap(() => fetchNamespaces(newValue as string));
          _options.unshift({
            label: 'All',
            value: 'all',
          });
          field.props.options = _options;
          states.value.context.searchFormValues['namespaceSelection'] = 'all';
        }
      }
    );
  }

  configs.value.namespace.allowedGlobalActions = listViewConfig.namespace.allowedGlobalActions;
  configs.value.namespace.searchForm = listViewConfig.namespace.searchForm;
  configs.value.namespace.searchFormOrigValues = structuredClone(listViewConfig.namespace.searchFormValues);
  configs.value.namespace.columns = listViewConfig.namespace.columns;

  states.value.role.searchFormValues = structuredClone(listViewConfig.role.searchFormValues);
  states.value.context.searchFormValues = structuredClone(listViewConfig.context.searchFormValues);
  states.value.namespace.searchFormValues = structuredClone(listViewConfig.namespace.searchFormValues);
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
});
const state = computed(() => states.value[props.objectType]);

const searchLimitReachedModalActive = ref(false);
const search = async (keepSelection = false, ignoreSearchLimit = false): Promise<void> => {
  const fetchResult = await standby.wrap(() =>
    fetchObjects(props.objectType, state.value.searchFormValues, ignoreSearchLimit ? undefined : appConfig.searchLimit)
  );
  if (!fetchResult) {
    searchLimitReachedModalActive.value = true;
    return;
  }
  if (fetchResult) {
    states.value[props.objectType].rows = fetchResult;
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
  }[props.objectType];
  router.push({
    name,
  });
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
    }[props.objectType];
    router.push({
      name,
      params: {
        id: ids[0],
      },
    });
  },
  canExecute: canDo('edit'),
  multi: false,
}));
const contextActions: ComputedRef<UGridContextAction[]> = computed(() => [editContextAction.value]);

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
</script>

<template>
  <main v-if="!loading" class="listView">
    <h1>
      {{ t(`ListView.heading.${objectType}`) }}
    </h1>
    <div class="routeButtonsWrapper">
      <div class="routeButtons">
        <RouterLink class="uButton" :class="{'uButton--flat': props.objectType !== 'role'}" to="/roles">
          {{ t('ListView.heading.role') }}
        </RouterLink>
        <RouterLink class="uButton" :class="{'uButton--flat': props.objectType !== 'namespace'}" to="/namespaces">
          {{ t('ListView.heading.namespace') }}
        </RouterLink>
        <RouterLink class="uButton" :class="{'uButton--flat': props.objectType !== 'context'}" to="/contexts">
          {{ t('ListView.heading.context') }}
        </RouterLink>
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
    <UConfirmDialog
      v-model:active="searchLimitReachedModalActive"
      :title="t('SearchLimitReachedModal.title')"
      :confirmLabel="t('SearchLimitReachedModal.button.confirm')"
      @confirm="search(false, true)"
    >
      <template #description>
        <p>
          {{ t('SearchLimitReachedModal.description', {limit: appConfig.searchLimit}) }}
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
  .routeButtons
    display: flex
    border: 1px solid var(--font-color-contrast-low)
    border-radius: var(--button-border-radius)
    overflow: hidden

    > .uButton
      text-decoration: none
      border-radius: 0
      padding: 0 calc(2 * var(--layout-spacing-unit))
</style>
