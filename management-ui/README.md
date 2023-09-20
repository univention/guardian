# Management UI

> The `yarn` command is used throughout this README (e.g., `yarn type-check`). You can find more examples of `yarn` commands in the `scripts` block of the `package.json`.

## Dev Requirements

- [Node.js](https://nodejs.org/en/) (18.x, LTS until 2023-10-24 and supported until 2025-04-30)
- [yarn](https://yarnpkg.com/getting-started/install)
  - We use `yarn` as package manager instead of `npm`
  - Enable corepack `corepack enable` to use `yarn` (`corepack` comes with Node.js)
    - Or if corepack doesn't work for you: `sudo npm install --global yarn` (`npm` comes with Node.js)

## Project Setup

```shell
yarn install
```

`yarn install` installs all dependencies of the package (defined by package.json) in the project directory.
The packages are installed only locally inside the `node_modules` folder.

**NOTE:** If you change git branches and things don't work correctly, try deleting your `node_modules` folder and re-running `yarn install`.

### Environment Variables

As part of the setup for the [main Guardian app](../README.md) you should have created an `.env` file.
The default already works out of the box.

Be sure to source your `.env` file before running the development server:

```shell
source ../.env
```

**NOTE:** All new environment variables need to be prefixed with `VITE` in order to be detected by the Management UI

Here are the variables you can set:

#### Settings Port

The settings port determines where the app's settings will come from.
Currently the only source is environment variables:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT=env
```

#### Authorization Port

The authorization port determines how the app will authorize the user.
By default, you get the in-memory adapter:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT=in_memory
export VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__IS_AUTHENTICATED=1
export VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__USERNAME=test-admin
```

You can test being unauthenticated by setting `VITE__IN_MEMORY_AUTHENTICATION_ADAPTER__IS_AUTHENTICATED=0`.

If you want to test against a keycloak instance, you can use an existing [RAM environment](https://jenkins2022.knut.univention.de/view/UCS@school/job/UCSschool-5.0/view/Environments/job/RAM-environment/) to bootstrap this.

1. Configure your `/etc/hosts` to point to the RAM instance:

   ```text
   10.207.16.184   primary.school.test ucs-sso.school.test ucs-sso-ng.school.test
   10.207.16.185   backup1.school.test
   ```

2. On the `primary.school.test` VM, run the following to create your client:

   ```shell
   /usr/share/ucs-school-ui-common/scripts/univention-create-keycloak-clients \
       --admin-password univention \
       --client-id guardian-management-ui-dev
   ```

3. Update your `.env` file:

   ```shell
   export VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT=keycloak
   export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__SSO_URI=https://ucs-sso-ng.school.test
   export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__REALM=ucs
   export VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__CLIENT_ID=guardian-management-ui-dev
   ```

#### Data Port

The data port pulls data from the API or a locally-generated in-memory store.

Currently, there is only the `in-memory` adapter:

```shell
export VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT=in_memory
```

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
export VITE__MANAGEMENT_UI__CORS__USE_PROXY=0
```

### Compile and Hot-Reload for Development

Run a hot-loading development server:

```shell
yarn dev
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
