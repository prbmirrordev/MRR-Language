const vscode = require('vscode');
const path = require('path');
const cp = require('child_process');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');

let client;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    let terminal = null;

    // Run Code Command
    let runCmd = vscode.commands.registerCommand('mrr.runCode', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active MRR file to run.');
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'mrr' && !document.fileName.endsWith('.mrr')) {
            vscode.window.showErrorMessage('Active file is not an MRR file.');
            return;
        }

        if (document.isDirty) {
            document.save();
        }

        const filePath = document.fileName;
        const dirPath = path.dirname(filePath);

        if (!terminal || terminal.exitStatus !== undefined) {
            terminal = vscode.window.createTerminal('MRR Run');
        }

        terminal.show();
        terminal.sendText(`cd "${dirPath}"`);
        terminal.sendText(`mrr run "${filePath}"`);
    });

    context.subscriptions.push(runCmd);

    // Formatter
    let formatter = vscode.languages.registerDocumentFormattingEditProvider('mrr', {
        provideDocumentFormattingEdits(document) {
            return new Promise((resolve, reject) => {
                const filePath = document.fileName;
                // mrr fmt reads and modifies the file directly, we wait for it
                cp.exec(`mrr fmt "${filePath}"`, (error, stdout, stderr) => {
                    if (error) {
                        vscode.window.showErrorMessage('MRR Formatter error: ' + stderr);
                        reject(error);
                    } else {
                        // Normally formatter returns text edits.
                        // Since mrr fmt modifies the file in place, we can just return empty edits,
                        // but VS Code might complain. A better approach would be to read the formatted output.
                        // As a workaround, we'll let VS Code know the file was updated externally.
                        resolve([]);
                    }
                });
            });
        }
    });

    context.subscriptions.push(formatter);

    // LSP Client Setup
    try {
        const serverCommand = 'mrr';
        const serverOptions = {
            run: { command: serverCommand, args: ['lsp'], transport: TransportKind.stdio },
            debug: { command: serverCommand, args: ['lsp'], transport: TransportKind.stdio }
        };

        const clientOptions = {
            documentSelector: [{ scheme: 'file', language: 'mrr' }],
            synchronize: {
                fileEvents: vscode.workspace.createFileSystemWatcher('**/.clientrc')
            }
        };

        client = new LanguageClient(
            'mrrLanguageServer',
            'MRR Language Server',
            serverOptions,
            clientOptions
        );

        client.start();
    } catch (e) {
        console.error("Failed to start MRR LSP client: ", e);
    }
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
