# Management UI

> The `yarn` command is used throughout this README (e.g., `yarn type-check`). You can find more examples of `yarn` commands in the `scripts` block of the `package.json`.

## Non-Dev Quickstart

If you are not doing development on the Management UI code, you can run the Management UI from docker in production mode.

Copy the `.env.example` file in the top-level guardian folder to an `.env` file, per the instructions in the [repository README](../README.md).
The defaults needed for this setup should already be correct:

```bash
export GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT=fast_api_oauth

export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__SSO_URI=http://traefik/guardian/keycloak
export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__REALM=GuardianDev
export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__CLIENT_ID=guardian
export VITE__API_DATA_ADAPTER__URI=http://localhost/guardian/management
export VITE__URL_SETTINGS_ADAPTER__CONFIG_URL=http://localhost/guardian/management-ui/config.json
```

Then run the [`dev-run`](../dev-run) script just as you would for other projects.

## Development Setup

### Requirements

- [Node.js](https://nodejs.org/en/) (18.x, LTS until 2023-10-24 and supported until 2025-04-30)
- [yarn](https://yarnpkg.com/getting-started/install)
  - We use `yarn` as package manager instead of `npm`
  - Enable corepack `corepack enable` to use `yarn` (`corepack` comes with Node.js)
    - Or if corepack doesn't work for you: `sudo npm install --global yarn` (`npm` comes with Node.js)

### Project Setup

```shell
yarn install
```

`yarn install` installs all dependencies of the package (defined by package.json) in the project directory.
The packages are installed only locally inside the `node_modules` folder.

**NOTE:** If you change git branches and things don't work correctly, try deleting your `node_modules` folder and re-running `yarn install`.

### Quickstart

As part of the setup for the [main Guardian app](../README.md) you should have created an `.env` file.
The default already works out of the box.

Source your `.env` file before running the development server:

```shell
source ../.env
```

Then run the development server:

```shell
yarn dev
```

The output of the command will tell you where to view the Management UI, usually at [localhost:5173/guardian/management-ui](http://localhost:5173/guardian/management-ui).

### Customizing Development Environment Variables

**NOTE:** All new environment variables need to be prefixed with `VITE` in order to be detected by the Management UI

Here are the variables you can set in your `.env` file:

#### Settings Port

The settings port determines where the app's settings will come from, either environment variables or a config hosted at a URL.

For local development, you usually want the `env` adapter to read directly from the sourced environment variables:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT=env
```

The `url` adapter is used in production/docker environments to read a config that is hosted at a given URL.
If you're doing development against this adapter, you need the following settings:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT=url
export VITE__MANAGEMENT_UI__CORS__USE_PROXY=1
export VITE__URL_SETTINGS_ADAPTER__CONFIG_URL=http://localhost/guardian/management-ui/config.json
```

Note that the config file in this example is being hosted in docker, so you'll also need to run [dev-run](../dev-run) if you're using the `url` adapter.

#### Authorization Port

The authorization port determines how the app will authorize the user.
By default, you get the in-memory adapter:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT=in_memory
export VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__IS_AUTHENTICATED=1
export VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__USERNAME=test-admin
```

You can test being unauthenticated by setting `VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__IS_AUTHENTICATED=0`.

If you want to test against the keycloak instance that is included in the `dev-compose.yaml` file in the top-level directory:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT=keycloak
export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__SSO_URI=http://traefik/guardian/keycloak
export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__REALM=GuardianDev
export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__CLIENT_ID=guardian
```

Testing against keycloak requires using [dev-run](../dev-run).

#### Data Port

The data port pulls data from the API or a locally-generated in-memory store.

Currently, the default is the `in-memory` adapter:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT=in_memory
```

For working with the Management API running in docker via [dev-run](../dev-run), you need the following settings:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT=api
export VITE__API_DATA_ADAPTER__URI=http://localhost/guardian/management
```

If you're working with a non-local instance of the Guardian backend, you can set up a proxy to avoid CORS errors:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT=api
export VITE__MANAGEMENT_UI__CORS__USE_PROXY=1
export VITE__API_DATA_ADAPTER__URI=https://primary.school.test/guardian/management
```

Please note that, depending on your setup in the Management API, you may need to configure the Keycloak authentication adapter as well.
The following setting disables Keycloak integration in the Management API:

```shell
export GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT=fast_api_always_authorized
```

Please see the instructions for configuring authentication in the top-level [repository README](../README.md) for more information.

#### CORS

When working with the backend, you may encounter CORS errors.
If you're using the local docker setup, please verify that you have the
following two settings:

```shell
export GUARDIAN__AUTHZ__CORS__ALLOWED_ORIGINS=*
export GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS=*
```

If you would like to develop against a remote server, you can enable a proxy that will make requests to the backend look like they're coming from the local server:

```shell
export VITE__MANAGEMENT_UI__CORS__USE_PROXY=1
```

### Use local univention-veb version

If you want to use a local version of `@univention/univention-veb` without using the Gitlab npm registry
you can do:

In a locally checked out [univention-veb](https://git.knut.univention.de/univention/univention-veb) repository:

```shell
yarn build
yarn pack
```

In the `management-ui` repository:

```shell
yarn remove @univention/univention-veb
yarn cache clean  # this is actually important since the cached tgz file is used even if version changes
# assumes that univention-veb is checked out in same folder as guardian
yarn add file:../../univention-veb/univention-univention-veb-vx.x.x.tgz
```

## Precommit / Code quality

### Type-Check

```shell
yarn type-check
```

### Lint with [ESLint](https://eslint.org/)

```shell
yarn lint
```

This will automatically fix some issues as part of the linting.

## Testing

### Run Unit Tests with [Vitest](https://vitest.dev/)

```shell
yarn test:unit
```

TODO: This does not work at the moment

## Testing the production build

Compile and minify for production:

```shell
yarn build
yarn preview  # You need to run `yarn build` beforehand manually
```

TODO: This does not work at the moment (the backend connection/config is not implemented yet)

## IDEs

### VSCode

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

If the standalone TypeScript plugin doesn't feel fast enough to you, Volar has also implemented a [Take Over Mode](https://github.com/johnsoncodehk/volar/discussions/471#discussioncomment-1361669) that is more performant. You can enable it by the following steps:

1. Disable the built-in TypeScript Extension
   1) Run `Extensions: Show Built-in Extensions` from VSCode's command palette
   2) Find `TypeScript and JavaScript Language Features`, right click and select `Disable (Workspace)`
2. Reload the VSCode window by running `Developer: Reload Window` from the command palette.

### WebStorm

[WebStorm](https://www.jetbrains.com/de-de/webstorm/) + [Vue setup](https://www.jetbrains.com/help/webstorm/vue-js.html#ws_vue_js_before_you_start)
