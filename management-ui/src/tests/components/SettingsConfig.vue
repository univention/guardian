<script lang="ts">
export default {
  name: 'SettingsConfig',
  props: {
    configObj: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <table class="config-display-table">
    <tr v-for="(item, key) in configObj" :key="key">
      <td>
        <label class="testLabel">{{ key }}:</label>
      </td>
      <td v-if="typeof item === 'object'">
        <SettingsConfig :configObj="item" />
      </td>
      <td v-else>{{ item }}</td>
    </tr>
  </table>
</template>

<style lang="stylus">
.config-display-table
  border: 1px solid
  margin: calc(2 * var(--layout-spacing-unit)) 0

  td
    padding: 0 calc(2 * var(--layout-spacing-unit))
</style>
