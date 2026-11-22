import * as vscode from "vscode";
import { openFile, placeCursor, run, sleep, waitFor } from "../helpers";
import type { Scene } from "../index";

/** Example: diagnostics, then a quick fix, asserted at each step. Copy it, rename it, change the file. */
export const diagnostics: Scene = {
  name: "diagnostics",
  async run() {
    const editor = await openFile("sample.txt");
    const uri = editor.document.uri;
    const [first] = await waitFor("diagnostics", () => {
      const found = vscode.languages.getDiagnostics(uri);
      return found.length ? found : undefined;
    });
    await run("workbench.actions.view.problems");
    await sleep(2000);

    placeCursor(editor, first.range.start.line, first.range.start.character);
    const actions = await vscode.commands.executeCommand<vscode.CodeAction[]>(
      "vscode.executeCodeActionProvider",
      uri,
      first.range
    );
    if (!actions?.length) {
      throw new Error("No quick fix is offered on the first diagnostic");
    }

    await run("editor.action.quickFix"); // the lightbulb menu, as a user opens it
    await sleep(1500);
    await run("acceptSelectedCodeAction");
    await waitFor("diagnostic cleared", () =>
      vscode.languages.getDiagnostics(uri).length < 1 ? true : undefined
    );
  },
};
