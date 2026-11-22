import * as vscode from "vscode";

export const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));
export const run = (id: string, ...args: unknown[]) => vscode.commands.executeCommand(id, ...args);
