import * as vscode from "vscode";

const SHOUT = /\b[A-Z]{5,}\b/g;

export function activate(context: vscode.ExtensionContext): void {
  const diagnostics = vscode.languages.createDiagnosticCollection("shoutLint");
  const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
  status.command = "shoutLint.report";
  status.show();

  const refresh = (document: vscode.TextDocument) => {
    const found: vscode.Diagnostic[] = [];
    for (const match of document.getText().matchAll(SHOUT)) {
      const start = document.positionAt(match.index!);
      const end = document.positionAt(match.index! + match[0].length);
      found.push(
        new vscode.Diagnostic(new vscode.Range(start, end), "Shouting", vscode.DiagnosticSeverity.Warning)
      );
    }

    diagnostics.set(document.uri, found);
    status.text = `$(megaphone) ${found.length}`;
  };

  context.subscriptions.push(
    diagnostics,
    status,
    vscode.workspace.onDidChangeTextDocument((event) => refresh(event.document)),
    vscode.languages.registerCodeActionsProvider("plaintext", {
      provideCodeActions(document, range) {
        const fix = new vscode.CodeAction("Lowercase this word", vscode.CodeActionKind.QuickFix);
        fix.edit = new vscode.WorkspaceEdit();
        fix.edit.replace(document.uri, range, document.getText(range).toLowerCase());
        return [fix];
      },
    }),
    vscode.languages.registerHoverProvider("plaintext", {
      provideHover(document, position) {
        if (!vscode.workspace.getConfiguration("shoutLint").get("hover.enabled")) return;

        const range = document.getWordRangeAtPosition(position);
        return range && new vscode.Hover("Reads as shouting.");
      },
    }),
    vscode.window.registerTreeDataProvider("shoutLint.findings", {
      getTreeItem: (item: string) => new vscode.TreeItem(item),
      getChildren: () => ["No findings yet"],
    }),
    vscode.commands.registerCommand("shoutLint.report", () => {
      const panel = vscode.window.createWebviewPanel(
        "shoutLintReport",
        "Shout Report",
        vscode.ViewColumn.Beside
      );
      panel.webview.html = "<h1>Shout report</h1>";
    }),
    vscode.commands.registerCommand("shoutLint.fixAll", () => vscode.window.showInformationMessage("Fixed"))
  );
}
