# Management UI

> The `yarn` command is used throughout this README (e.g., `yarn type-check`). You can find more examples of `yarn` commands in the `scripts` block of the `package.json`.

## Dev Requirements

- [Node.js](https://nodejs.org/en/) (18.x, LTS until 2023-10-24 and supported until 2025-04-30)
- [yarn](https://yarnpkg.com/getting-started/install)
  - We use `yarn` as package manager instead of `npm`
  - Installation: `sudo npm install --global yarn`
    - `npm` comes with Node.js

## Project Setup

```shell
yarn install
```

`yarn install` installs all dependencies of the package (defined by package.json) in the project directory.
The packages are installed only locally inside the `node_modules` folder.

**NOTE:** If you change git branches and things don't work correctly, try deleting your `node_modules` folder and re-running `yarn install`.

### Compile and Hot-Reload for Development

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