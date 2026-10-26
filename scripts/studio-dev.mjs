import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const localPython = path.join(root, '.venv-studio', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = process.env.DOCOS_STUDIO_PYTHON || (existsSync(localPython) ? localPython : 'python3');
const apiPort = process.env.DOCOS_API_PORT || '8876';
const portIndex = process.argv.indexOf('--port');
const frontPort = portIndex >= 0 ? process.argv[portIndex + 1] : process.env.PORT || '3000';
const children = [];
let closing = false;
function stop(code = 0) {
  if (closing) return;
  closing = true;
  for (const child of children) child.kill('SIGTERM');
  setTimeout(() => process.exit(code), 500).unref();
}
function launch(command, args) {
  const child = spawn(command, args, { cwd: root, stdio: 'inherit', env: { ...process.env, DOCOS_API_PORT: apiPort } });
  children.push(child);
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', code => { if (!closing) stop(code || 0); });
}
launch(python, ['-m', 'uvicorn', 'studio_api.app:create_app', '--factory', '--host', '127.0.0.1', '--port', apiPort]);
launch(process.execPath, [path.join(root, 'apps/studio/node_modules/vite/bin/vite.js'), '--config', 'apps/studio/vite.config.ts', '--host', '0.0.0.0', '--port', frontPort, '--strictPort']);
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
