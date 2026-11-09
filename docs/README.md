# Develop the pulseplot website

Edit the files in `docs/src`. The build produces `docs/index.html`, a standalone
page with inline JavaScript and CSS. You can open that file directly or serve
the `docs` directory through GitHub Pages.

## Preview changes

Use Node.js 22 or newer. Run these commands from the repository root.
The source preview requires no package installation.

```sh
node docs/scripts/dev.mjs
```

Open <http://127.0.0.1:4173/> to preview the source modules. Refresh the page after
you edit a file. Browser developer tools show the original module filenames and
line numbers. Set `PORT` to use a different port.

Open <http://127.0.0.1:4173/index.html> to check the generated document. Rebuild
that document before checking changes there.

## Build and test

Install the development dependencies with pnpm 11:

```sh
pnpm --dir docs install --frozen-lockfile --ignore-scripts
```

The locked esbuild package supplies its platform binary through an optional
dependency. Its install script is not needed for the build.

Generate the document:

```sh
node docs/scripts/build.mjs
```

Run the website tests:

```sh
node --test docs/tests/*.test.mjs
```

Check whether the generated document matches the sources:

```sh
node docs/scripts/build.mjs --check
```

For browser regression tests, install Chromium once:

```sh
pnpm --dir docs exec playwright install chromium
```

Then run:

```sh
pnpm --dir docs test:browser
```

The browser suite tests source modules, the generated page over HTTP, and the
generated page opened directly from disk. It covers templates, editing, batch
changes, undo/redo, saved projects, JSON import, Python downloads, and image exports.
To use an installed Chrome or Chromium binary, set
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` to its absolute path.

Commit `docs/index.html` with your source changes. The test suite checks the
generated document and compares all four templates' Python output against
fixtures captured from the original page. It also covers project normalization,
selection, overlap detection, gaps, snapping, pulse shapes, and the preview server.

You can also run `pnpm dev`, `pnpm build`, `pnpm test`, or `pnpm check` from
`docs`. With npm, run `npm install` in `docs` first and use the corresponding
`npm run` commands.

## Choose a source file

| File | Responsibility |
| --- | --- |
| `src/index.html` | Page structure and accessible control labels |
| `src/styles/studio.css` | Theme, layout, controls, and canvas styles |
| `src/styles/responsive.css` | Layout rules for smaller screens |
| `src/app.js` | Restore the saved project, bind events, and render |
| `src/config.js` | Defaults, shape parameters, and math symbols |
| `src/state.js` | Current project and transient editor state |
| `src/model.js` | Project normalization, selection, gaps, and validation |
| `src/history.js` | Saved-project loading and undo/redo |
| `src/commands.js` | Add, delete, duplicate, copy, paste, and load templates |
| `src/shapes.js` | Pulse envelope sampling and interpolation |
| `src/snapping.js` | Grid and magnetic alignment |
| `src/svg.js`, `src/canvas.js` | SVG helpers, canvas geometry, and drawing |
| `src/render.js` | Render scheduling, local saves, channels, settings, and code output |
| `src/inspector.js` | Single-element and batch editing controls |
| `src/interactions.js` | Canvas dragging, resizing, drops, and shape editing |
| `src/events.js` | DOM event listeners and keyboard shortcuts |
| `src/python.js` | Python generation and syntax highlighting |
| `src/exports.js` | SVG, PNG, and file downloads |
| `src/math.js`, `src/utils.js`, `src/notifications.js` | Text formatting, shared helpers, and toasts |
| `src/templates.js`, `src/templates/` | Template registry and example projects |

## Add a feature

Add the behavior to the relevant module, then connect its controls in
`src/events.js`. Keep calculations independent of the DOM when possible so tests
can import them directly. Replace an entire project through `setState` so all
modules retain the same live reference. Keep temporary interaction state in
`runtime`; saved project data belongs in `state`.

To add a template, create a named export in `src/templates/`, register it in
`src/templates.js`, and add an option to `src/index.html`. Add a Python fixture
and regression test for its expected output.

Use JavaScript modules with explicit imports and exports. esbuild follows imports
from `src/app.js`, preserves module scopes, and bundles the code for browsers.
The build inlines the bundle and both stylesheets in `docs/index.html`.
The generated page has no runtime package dependencies or network requests.
Keep startup calls in `src/app.js`. Use the source preview to debug individual files.

Add regression tests in `docs/tests`, then rebuild and run the checks above.

## Publish the generated page

For GitHub Pages, select **Deploy from a branch** in the repository's Pages
settings, choose your publishing branch, and choose **/docs** as the folder.
`docs/.nojekyll` disables Jekyll processing. Publishing settings remain under
your control.
