import {createRouter, createWebHistory} from 'vue-router';
import ListView from '@/views/ListView.vue';
import EditView from '@/views/EditView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/roles',
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
    {
      path: '/roles/edit/:id/:page?',
      name: 'editRole',
      component: EditView,
      props: {action: 'edit', objectType: 'role'},
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
  ],
});

export default router;