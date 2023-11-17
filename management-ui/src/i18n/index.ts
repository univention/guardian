import i18next from 'i18next';

import de from '@/i18n/locales/de.json';
import en from '@/i18n/locales/en.json';
import univentionVebOverwriteDE from '@/i18n/univentionVebOverwrites/de.json';
import univentionVebOverwriteEN from '@/i18n/univentionVebOverwrites/en.json';
import {getCookie} from '@/helpers/cookies';

// TODO: In the future, we may want to parse /univention/languages.json
// to get which languages are installed on the system.
// Since Guardian only currently supports English and German,
// this list can be hardcoded for now.
const availableLanguages = ['en', 'de'];

const i18nParameters = ((): {lng: string; fallbackLng: string[]} => {
  const locale = getCookie('UMCLang') || window.navigator.language || 'en-US';
  const lang = locale.slice(0, 2);
  return {
    lng: lang,
    fallbackLng: availableLanguages,
  };
})();

export const i18nInitialized = i18next.init({
  defaultNS: 'management-ui',
  interpolation: {
    skipOnVariables: false,
  },
  debug: true,
  resources: {},
  ...i18nParameters,
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
