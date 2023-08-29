<script setup lang="ts">
import {ref, onMounted} from 'vue';

const loading = ref(true);

onMounted(async () => {
  loading.value = false;
});
</script>

<template>
  <main v-if="!loading" class="testView">
    <h1><RouterLink :to="{name: 'testsMain'}">Manual Tests</RouterLink></h1>
    <ul>
      <li><RouterLink :to="{name: 'testsAuthenticationAdapter'}">Authentication Adapter Tests</RouterLink></li>
    </ul>
  </main>
</template>

<style lang="stylus">
main.testView
  padding: calc(4 * var(--layout-spacing-unit))
  margin: 0 auto
  height: 100vh
  display: flex
  flex-direction: column
</style>
