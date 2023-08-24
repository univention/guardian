import i18next from 'i18next';

import de from '@/i18n/locales/de.json';
import en from '@/i18n/locales/en.json';
import univentionVebOverwriteDE from '@/i18n/univentionVebOverwrites/de.json';
import univentionVebOverwriteEN from '@/i18n/univentionVebOverwrites/en.json';

export const i18nInitialized = i18next.init({
  lng: 'de',
  defaultNS: 'management-ui',
  fallbackLng: 'en',
  interpolation: {
    skipOnVariables: false,
  },
  debug: true,
  resources: {},
});

export const loadTranslations = function (): void {
  if (!i18next.isInitialized) {
    throw Error('You cannot load translations before i18next was initialized!');
  }
  i18next.addResourceBundle('de', 'management-ui', de);
  i18next.addResourceBundle('en', 'management-ui', en);
  i18next.addResourceBundle('de', 'univention-veb', univentionVebOverwriteDE, true, true);
  i18next.addResourceBundle('en', 'univention-veb', univentionVebOverwriteEN, true, true);
};
