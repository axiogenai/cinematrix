const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Parse CLI flags
function getArg(flag, defaultVal) {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && process.argv[idx + 1] ? process.argv[idx + 1] : defaultVal;
}

const HTML_FILE = getArg('--html', '');
const AUDIO_FILE = getArg('--audio', '');
const OUTPUT_FILE = getArg('--output', 'output.mp4');
const FPS = parseInt(getArg('--fps', '30'), 10);
const DURATION = parseFloat(getArg('--duration', '15.0'));
const WIDTH = parseInt(getArg('--width', '1920'), 10);
const HEIGHT = parseInt(getArg('--height', '1080'), 10);
const FFMPEG_PATH = getArg('--ffmpeg', 'C:\\Users\\aditya\\node_modules\\ffmpeg-static\\ffmpeg.exe');

// Detect Chrome
const CHROME_CANDIDATES = [
  'C:\\Users\\aditya\\AppData\\Local\\ms-playwright\\chromium-1234\\chrome-win64\\chrome.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
];
let CHROME_PATH = CHROME_CANDIDATES.find(p => fs.existsSync(p));

if (!CHROME_PATH) {
  console.error(JSON.stringify({ status: 'error', message: 'No Chrome or Chromium executable found.' }));
  process.exit(1);
}

const TOTAL_FRAMES = Math.ceil(DURATION * FPS);

async function render() {
  const startTime = Date.now();

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      `--window-size=${WIDTH},${HEIGHT}`
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });

  const resolvedHtml = 'file:///' + path.resolve(HTML_FILE).replace(/\\/g, '/');
  await page.goto(resolvedHtml, { waitUntil: 'networkidle0' });

  // Wait for fonts
  try {
    await page.waitForFunction(() => window.fontsReady === true, { timeout: 8000 });
  } catch (e) {
    // Continue if timeout
  }

  // FFmpeg Arguments
  const ffmpegArgs = [
    '-y',
    '-f', 'image2pipe',
    '-vcodec', 'mjpeg',
    '-r', String(FPS),
    '-i', '-'
  ];

  if (AUDIO_FILE && fs.existsSync(AUDIO_FILE)) {
    ffmpegArgs.push('-i', AUDIO_FILE);
  }

  ffmpegArgs.push(
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '17',
    '-pix_fmt', 'yuv420p'
  );

  if (AUDIO_FILE && fs.existsSync(AUDIO_FILE)) {
    ffmpegArgs.push('-c:a', 'aac', '-b:a', '256k', '-shortest');
  }

  ffmpegArgs.push(OUTPUT_FILE);

  const ffmpeg = spawn(FFMPEG_PATH, ffmpegArgs);
  let ffmpegErr = '';
  ffmpeg.stderr.on('data', d => { ffmpegErr += d.toString(); });

  const ffmpegPromise = new Promise((resolve, reject) => {
    ffmpeg.on('close', code => {
      if (code === 0) resolve();
      else reject(new Error(`FFmpeg error (code ${code}): ${ffmpegErr}`));
    });
    ffmpeg.on('error', reject);
  });

  let lastReport = Date.now();

  for (let frame = 0; frame < TOTAL_FRAMES; frame++) {
    const t = Math.min(frame / FPS, DURATION);
    await page.evaluate(time => window.renderAt(time), t);

    const buf = await page.screenshot({
      type: 'jpeg',
      quality: 95
    });

    if (!ffmpeg.stdin.write(buf)) {
      await new Promise(r => ffmpeg.stdin.once('drain', r));
    }

    if (Date.now() - lastReport > 600 || frame === TOTAL_FRAMES - 1) {
      lastReport = Date.now();
      const elapsed = (Date.now() - startTime) / 1000;
      const currentFps = (frame + 1) / Math.max(0.001, elapsed);
      const percent = Math.min(99, Math.round(((frame + 1) / TOTAL_FRAMES) * 100));
      const eta = (TOTAL_FRAMES - frame - 1) / Math.max(0.001, currentFps);

      console.log(JSON.stringify({
        status: 'rendering',
        frame: frame + 1,
        total_frames: TOTAL_FRAMES,
        percent: percent,
        fps: Math.round(currentFps * 10) / 10,
        eta_seconds: Math.round(eta * 10) / 10,
        message: `Rendering frame ${frame + 1}/${TOTAL_FRAMES} via Chromium GPU Pipeline (${Math.round(currentFps)} fps)`
      }));
    }
  }

  ffmpeg.stdin.end();
  await ffmpegPromise;
  await browser.close();

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  const sizeBytes = fs.existsSync(OUTPUT_FILE) ? fs.statSync(OUTPUT_FILE).size : 0;

  console.log(JSON.stringify({
    status: 'completed',
    percent: 100,
    total_time: totalTime,
    output_mp4: OUTPUT_FILE,
    file_size_bytes: sizeBytes,
    message: `Master video rendered successfully (${totalTime}s)`
  }));
}

render().catch(err => {
  console.error(JSON.stringify({ status: 'failed', error: err.message }));
  process.exit(1);
});
