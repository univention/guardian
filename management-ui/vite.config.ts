import {fileURLToPath, URL} from 'node:url';
import {readFile} from 'fs/promises';
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
  if (mode === 'development' || mode === 'test') {
    const env = loadEnv(mode, process.cwd(), '');
    if (env.VITE_USE_REAL_BACKEND === 'true') {
      const appConfigFile: string = await readFile(fileURLToPath(new URL('./public/config.json', import.meta.url)), {encoding: 'utf-8'});
      const appConfig = JSON.parse(appConfigFile);
      config.server = {
        proxy: {
          '/ucsschool/guardian': { // TODO use correct backend url
            target: appConfig['backendURL'],
            changeOrigin: false, // let the bff link back to this proxy in the absolute url values
            secure: false,
          },
        },
      };
    }
  }
  return config;
});
