import {createApp} from 'vue';
import I18NextVue from 'i18next-vue';
import i18next from 'i18next';
import {createPinia} from 'pinia';

import '@univention/univention-veb/style.css';

import App from '@/App.vue';
import router from '@/router';

import {i18nInitialized, loadTranslations} from '@/i18n';
import {UniventionVebPlugin} from '@univention/univention-veb';

const pinia = createPinia();
i18nInitialized.then(() => {
  document.documentElement.setAttribute('lang', i18next.language);
  const app = createApp(App).use(router).use(I18NextVue, {i18next}).use(UniventionVebPlugin, {i18next}).use(pinia);

  app.mount('#app');
  loadTranslations();
});
