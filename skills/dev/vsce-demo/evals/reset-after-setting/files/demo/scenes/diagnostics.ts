import * as vscode from "vscode";
import { run, sleep } from "../helpers";

export const diagnostics = {
  name: "diagnostics",
  async run() {
    const [uri] = await vscode.workspace.findFiles("sample.txt");
    await vscode.window.showTextDocument(uri);
    if (!vscode.languages.getDiagnostics(uri).length) throw new Error("no diagnostics");

    await run("workbench.actions.view.problems");
    await sleep(2000);
  },
};
