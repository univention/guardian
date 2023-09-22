/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT: 'url' | 'env';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
