import {createRouter, createWebHistory} from 'vue-router';
import ListView from '@/views/ListView.vue';
import EditView from '@/views/EditView.vue';
import TestView from '@/tests/views/TestView.vue';
import SettingsAdapterTestView from '@/tests/views/SettingsAdapter.vue';
import AuthenticationAdapterTestView from '@/tests/views/AuthenticationAdapter.vue';

const testRoutes = (() => {
  if (import.meta.env.VITE__MANAGEMENT_UI__TESTING__ENABLE_TEST_ROUTES !== '1') {
    return [];
  }

  return [
    {
      path: '/tests',
      name: 'testsMain',
      component: TestView,
    },
    {
      path: '/tests/settings-adapter',
      name: 'testsSettingsAdapter',
      component: SettingsAdapterTestView,
    },
    {
      path: '/tests/authentication-adapter',
      name: 'testsAuthenticationAdapter',
      component: AuthenticationAdapterTestView,
    },
  ];
})();

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      redirect: {name: 'listRoles'},
    },
    {
      path: '/roles',
      name: 'listRoles',
      component: ListView,
      props: {objectType: 'role'},
    },
    {
      path: '/roles/add/:page?',
      name: 'addRole',
      component: EditView,
      props: {action: 'add', objectType: 'role'},
    },
    /*
    {
      path: '/roles/edit/:id/:page?',
      name: 'editRole',
      component: EditView,
      props: {action: 'edit', objectType: 'role'},
    },
    */
    {
      path: '/roles/edit/:id/:page?',
      name: 'editRole',
      component: EditView,
      props: {action: 'edit', objectType: 'role'},
      children: [
        {
          name: 'listCapabilities',
          path: 'capabilties',
          component: ListView,
          props: {objectType: 'capability'},
        },
        {
          name: 'addCapability',
          path: 'capabilties/add/:page?',
          component: EditView,
          props: {action: 'add', objectType: 'capability'},
        },
        {
          name: 'editCapability',
          path: 'capabilties/edit/:id2/:page?',
          component: EditView,
          props: {action: 'edit', objectType: 'capability'},
        },
      ],
    },
    {
      path: '/namespaces',
      name: 'listNamespaces',
      component: ListView,
      props: {objectType: 'namespace'},
    },
    {
      path: '/namespaces/add/:page?',
      name: 'addNamespace',
      component: EditView,
      props: {action: 'add', objectType: 'namespace'},
    },
    {
      path: '/namespaces/edit/:id/:page?',
      name: 'editNamespace',
      component: EditView,
      props: {action: 'edit', objectType: 'namespace'},
    },
    {
      path: '/contexts',
      name: 'listContexts',
      component: ListView,
      props: {objectType: 'context'},
    },
    {
      path: '/contexts/add/:page?',
      name: 'addContext',
      component: EditView,
      props: {action: 'add', objectType: 'context'},
    },
    {
      path: '/contexts/edit/:id/:page?',
      name: 'editContext',
      component: EditView,
      props: {action: 'edit', objectType: 'context'},
    },
    ...testRoutes,
  ],
});

export default router;
