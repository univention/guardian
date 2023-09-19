import {fileURLToPath, URL} from 'node:url';
import {defineConfig, loadEnv, type UserConfig} from 'vite';
import vue from '@vitejs/plugin-vue';

// https://github.com/vitejs/vite/issues/2245
import pluginRewriteAll from 'vite-plugin-rewrite-all';

// https://vitejs.dev/config/
export default defineConfig(async({mode}) => {
  const config: UserConfig = {
    plugins: [vue(), pluginRewriteAll()],
    base: '/guardian/management-ui/',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  };

  // If doing development against an external server,
  // you can use a proxy to avoid getting a CORS errors.
  // It's not needed if you're working against a local docker version of
  // the Guardian backend and you have `GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS=*`.
  if (mode === 'development' || mode === 'test') {
    const env = loadEnv(mode, process.cwd(), '');
    if (env.VITE__MANAGEMENT_UI__CORS__USE_PROXY === '1') {
      const backendUri = new URL(env.VITE__API_DATA_ADAPTER__URI.replace(/\/$/, ''));
      config.server = {
        proxy: {
          [`^${backendUri.pathname}/`]: {
            target: `${backendUri.origin}`,
            changeOrigin: false, // let the bff link back to this proxy in the absolute url values
            secure: false,
          },
        },
      };
    }
  }

  return config;
});
