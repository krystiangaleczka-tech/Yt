import {existsSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const python=resolve(root,'.venv-studio',process.platform==='win32'?'Scripts/python.exe':'bin/python');
if(!existsSync(python)||!existsSync(resolve(root,'apps/studio/dist/index.html'))){
  console.error('Najpierw wykonaj: python3 scripts/install_studio.py (Windows: python scripts/install_studio.py)');process.exit(1);
}
const child=spawn(python,['-m','studio_api',...process.argv.slice(2)],{cwd:root,stdio:'inherit'});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>child.kill(signal));
child.on('exit',code=>process.exit(code??1));
