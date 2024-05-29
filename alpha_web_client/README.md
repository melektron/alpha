# Alpha Web Client

This is the main web-application that will contain all the future functionality of the alpha toolset.

Current features:

- KaYeet client
- DevTools:
  - WebSocket test
  - VueJS reactivity test

Currently, when opening the webpage the router automatically moves to the KaYeet route, as that is the only proper feature of the app.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

Output will be in "dist" folder. It's content can then be hosted by any webserver. For routing and reloads to work properly, the server should be configured to return "index.html" for any requested URL.