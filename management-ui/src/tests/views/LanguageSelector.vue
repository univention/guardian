<script setup lang="ts">
import {ref, type Ref, onMounted} from 'vue';
import {UButton} from '@univention/univention-veb';
import {getCookie} from '@/helpers/cookies';

const loading = ref(true);

const en = 'en-US';
const de = 'de-DE';
const lang: Ref<'en-US' | 'de-DE' | ''> = ref('');

const setI18nCookie = () => {
  document.cookie = `UMCLang=${lang.value}; path=/univention/; SameSite=Strict`;
};
const useEnglish = () => {
  lang.value = en;
  setI18nCookie();
};
const useGerman = () => {
  lang.value = de;
  setI18nCookie();
};
const clearLanguage = () => {
  lang.value = '';
  setI18nCookie();
};
const useCurrentLanguage = () => {
  const currentLang = (getCookie('UMCLang') || '').slice(0, 2);
  switch (currentLang) {
    case 'en':
      useEnglish();
      return;
    case 'de':
      useGerman();
      return;
    default:
      clearLanguage();
  }
};

onMounted(() => {
  useCurrentLanguage();
  loading.value = false;
});
</script>

<template>
  <main
    v-if="!loading"
    class="testView"
  >
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>

    <h2>Language Tests</h2>

    <div class="testWrapper">
      <div class="uContainer uCard listDisplay">
        <p>Switch the language of the UI, without the need for the Portal</p>

        <div class="testButtonsWrapper">
          <UButton
            :class="{'uButton--flat': lang !== en}"
            type="button"
            label="English"
            @click="useEnglish"
          />
          <UButton
            :class="{'uButton--flat': lang !== de}"
            type="button"
            label="German"
            @click="useGerman"
          />
          <UButton
            :class="{'uButton--flat': lang !== ''}"
            type="button"
            label="None"
            @click="clearLanguage"
          />
        </div>

        <p>
          <RouterLink
            :to="{name: 'landing'}"
            target="_blank"
          >
            View Language in App
          </RouterLink>
        </p>
      </div>
    </div>
  </main>
</template>
