// Fixed entry point and trusted, server-produced JSON. No user-supplied JavaScript.
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderMedia, ensureBrowser, makeCancelSignal } from '@remotion/renderer';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
if (process.argv[2] === '--setup') {
  const browser = await ensureBrowser({browserExecutable:process.env.DOCOS_REMOTION_BROWSER || undefined});
  console.log(JSON.stringify(browser));
} else {
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) throw new Error('Expected input JSON and output MP4');
  const input = JSON.parse(await readFile(inputPath,'utf8'));
  const { cancelSignal, cancel } = makeCancelSignal();
  process.on('SIGTERM',()=>{cancel();});
  process.on('SIGINT',()=>{cancel();});
  const report = (progress,message)=>console.log(JSON.stringify({progress,message}));
  report(.03,'Przygotowanie szablonu Remotion');
  const serveUrl = await bundle({entryPoint:path.join(root,'src/motion/entry.tsx'),
    publicDir:path.join(path.dirname(inputPath),'public'),
    outDir:path.join(path.dirname(inputPath),'bundle'), onProgress: n=>report(.03+n/100*.12,'Budowanie kompozycji')});
  const composition = {id:'DocosInsert',width:input.width,height:input.height,fps:input.fps,
    durationInFrames:input.insert.duration,defaultProps:{},props:{insert:input.insert,imageUrls:input.imageUrls}};
  await renderMedia({serveUrl,composition,inputProps:composition.props,outputLocation:outputPath,codec:'h264',
    pixelFormat:'yuv420p',crf:18,concurrency:2,cancelSignal,
    browserExecutable:process.env.DOCOS_REMOTION_BROWSER || undefined,
    onProgress:({progress})=>report(.15+progress*.8,'Renderowanie wstawki')});
  report(.95,'Sprawdzanie pliku');
}
