#!/usr/bin/env node
/**
 * Export Reel-Vigente-9x16.html → MP4 (1080×1920, H.264) for Instagram Reels.
 *
 * Requires: Node 18+, ffmpeg on PATH.
 *   brew install ffmpeg
 *   npm install && npx playwright install chromium
 *   npm run export
 */
import { chromium } from 'playwright';
import { spawnSync } from 'node:child_process';
import { mkdir, readdir, rename, unlink } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REEL_HTML = path.join(__dirname, 'Reel-Vigente-9x16.html');
const OUT_MP4 = path.join(__dirname, 'Reel-Vigente-9x16.mp4');
const TMP_DIR = path.join(__dirname, '.export-tmp');

function requireFfmpeg() {
  const r = spawnSync('ffmpeg', ['-version'], { encoding: 'utf8' });
  if (r.status !== 0) {
    console.error('ffmpeg no encontrado. Instala con: brew install ffmpeg');
    process.exit(1);
  }
}

async function findWebm(dir) {
  const files = await readdir(dir);
  const webm = files.filter((f) => f.endsWith('.webm'));
  if (!webm.length) throw new Error('Playwright no generó .webm');
  return path.join(dir, webm[0]);
}

async function main() {
  requireFfmpeg();
  await mkdir(TMP_DIR, { recursive: true });

  const reelUrl = `file://${REEL_HTML}?export=1`;
  console.log('Grabando reel…', reelUrl);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
    recordVideo: { dir: TMP_DIR, size: { width: 1080, height: 1920 } },
  });
  const page = await context.newPage();
  page.setDefaultTimeout(120_000);
  await page.goto(reelUrl, { waitUntil: 'load' });
  const totalMs = await page.evaluate(() => window.HV_REEL?.totalMs ?? 36_000);
  await page.waitForFunction(() => window.HV_REEL?.cycleComplete === true, { timeout: totalMs + 30_000 });
  await page.waitForTimeout(1_500);

  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();

  const webm = video ? await video.path() : await findWebm(TMP_DIR);
  console.log('Convirtiendo a MP4…');

  const r = spawnSync(
    'ffmpeg',
    ['-y', '-i', webm, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-an', OUT_MP4],
    { stdio: 'inherit' },
  );
  if (r.status !== 0) process.exit(r.status ?? 1);

  await unlink(webm).catch(() => {});
  console.log('Listo:', OUT_MP4);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});