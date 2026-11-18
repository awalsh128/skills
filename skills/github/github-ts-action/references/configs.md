# Config templates

Adapted from the exemplar. Replace names, check dependency versions with `npm view`, and drop what the action
does not need.

## action.yml

```yaml
name: "<Display Name>"
description: "<One sentence.>"
author: <owner>
branding:
  icon: "hard-drive" # any Feather icon
  color: "green"

inputs:
  <snake_case_name>:
    description: "<What it does. State the format and allowed values.>"
    required: false
    default: ""
outputs:
  <kebab-case-name>:
    description: "<What it holds and its format.>"

runs:
  using: "node24"
  main: "dist/action/index.js"
```

## tsconfig

`tsconfig.base.json`: `target`/`lib` `ES2023`, `module`/`moduleResolution` `nodenext`, `strict`,
`noUncheckedIndexedAccess`, `declaration`, `sourceMap`, `esModuleInterop`, `forceConsistentCasingInFileNames`,
`skipLibCheck`.

- `tsconfig.json` (typecheck, `noEmit`, `allowImportingTsExtensions`, `types: ["node"]`): extends base,
  includes `src`, `test`, `scripts`.
- `tsconfig.build.json` (emit): extends base, includes `src` only, `rootDir: "."`, `outDir: "./dist"`,
  `declarationMap`.
- `tsconfig.scripts.json` (`.mts` tooling, `--noEmit`): extends base, includes `scripts`.

## rollup.config.mjs

```js
import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import { nodeResolve } from "@rollup/plugin-node-resolve";

/** Bundles the action and its dependencies into dist/action/index.js. */
export default {
  input: "dist/src/index.js", // tsc output, so TypeScript compiles one way
  output: {
    file: "dist/action/index.js",
    format: "es",
    sourcemap: true,
    // Some CommonJS dependencies call require() at runtime.
    banner:
      "import { createRequire as __createRequire } from 'node:module';\n" +
      "const require = __createRequire(import.meta.url);",
  },
  plugins: [nodeResolve({ preferBuiltins: true, exportConditions: ["node"] }), commonjs(), json()],
  onwarn(warning, warn) {
    // Third-party noise only; never swallow warnings from our own code.
    const fromDependency = (warning.ids ?? [warning.id ?? ""]).every((id) => id.includes("node_modules"));
    if (
      warning.code === "THIS_IS_UNDEFINED" ||
      (fromDependency && ["INVALID_ANNOTATION", "CIRCULAR_DEPENDENCY"].includes(warning.code))
    ) {
      return;
    }

    warn(warning);
  },
};
```

If the bundle needs non-JS files at runtime, add a plugin whose `writeBundle()` does
`fs.cpSync(src, dest, { recursive: true })`.

## vitest.config.ts

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["test/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "json"],
      reportsDirectory: "coverage",
      include: ["src/**/*.ts"],
      exclude: ["src/index.ts"],
    },
  },
});
```

## eslint.config.js, .prettierrc.json, .node_ver

```js
import tsParser from "@typescript-eslint/parser";

export default [
  { ignores: ["dist/**", "node_modules/**"] },
  {
    files: ["src/**/*.ts", "test/**/*.ts", "scripts/**/*.ts", "scripts/**/*.mts"],
    languageOptions: { parser: tsParser, ecmaVersion: "latest", sourceType: "module" },
    rules: {},
  },
];
```

`.prettierrc.json`: `{ "printWidth": 110 }`. `.node_ver`: `24`.

## package.json scripts

```json
{
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": {
    "runall": "node ./node_modules/npm-run-all/bin/npm-run-all/index.js",
    "build:lib": "tsc -p tsconfig.build.json",
    "bundle": "rollup -c rollup.config.mjs",
    "build": "npm run -s runall -- build:lib bundle build:scripts",
    "clean": "rm -rf dist coverage",
    "lint": "eslint src test scripts --ext .ts,.mts",
    "typecheck": "npm run -s runall -- typecheck:lib typecheck:scripts",
    "test": "vitest run --coverage",
    "release": "semantic-release",
    "release:dry-run": "semantic-release --dry-run"
  }
}
```

Also `prepare: husky`, `typecheck:lib`, `typecheck:scripts`, `build:scripts`, and `check:*` scripts for repo
checks. Set `"version": "0.0.0-semantically-released"` and a `funding` block pointing at the owner's Sponsors
page. `.gitignore`: `dist/`, `coverage/`, `node_modules/`.
