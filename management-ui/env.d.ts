/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_REAL_BACKEND: 'true' | 'false';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
