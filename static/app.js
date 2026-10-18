// CineMatrix AI — Media Studio Professional Client Engine
// Complete, Dynamic, Non-Hardcoded Video Production Controller

let currentStoryboard = null;
let activeJobId = null;
let pollTimer = null;
let lastLoggedJobMessage = '';
let activeStageHtmlUrl = null;
let vaultVideosCache = [];

// DOM Elements: Topbar & Settings
const presetSelect = document.getElementById('presetSelect');
const toggleVaultBtn = document.getElementById('toggleVaultBtn');
const vaultCount = document.getElementById('vaultCount');
const directorStatusDot = document.getElementById('directorStatusDot');
const directorStatusText = document.getElementById('directorStatusText');
const activeEngineLabel = document.getElementById('activeEngineLabel');

// DOM Elements: Creative Brief & Production Settings
const promptInput = document.getElementById('promptInput');
const aspectRatioSelect = document.getElementById('aspectRatioSelect');
const durationSelect = document.getElementById('durationSelect');
const fpsSelect = document.getElementById('fpsSelect');
const moodSelect = document.getElementById('moodSelect');
const engineSelect = document.getElementById('engineSelect');
const engineDescription = document.getElementById('engineDescription');
const engineBadgeInfo = document.getElementById('engineBadgeInfo');
const generateStoryboardBtn = document.getElementById('generateStoryboardBtn');
const timelineStatsBadge = document.getElementById('timelineStatsBadge');

// DOM Elements: Timeline & Scene Editor
const scenesContainer = document.getElementById('scenesContainer');
const sceneCount = document.getElementById('sceneCount');
const addSceneBtn = document.getElementById('addSceneBtn');
const clearScenesBtn = document.getElementById('clearScenesBtn');
const startRenderBtn = document.getElementById('startRenderBtn');
const footerEstTime = document.getElementById('footerEstTime');

// DOM Elements: Viewport & Player Stage
const playerFrame = document.getElementById('playerFrame');
const masterVideoPlayer = document.getElementById('masterVideoPlayer');
const videoSource = document.getElementById('videoSource');
const emptyPlayerState = document.getElementById('emptyPlayerState');
const activeVideoTitle = document.getElementById('activeVideoTitle');
const activeVideoAspect = document.getElementById('activeVideoAspect');
const activeVideoResolution = document.getElementById('activeVideoResolution');
const activeVideoDuration = document.getElementById('activeVideoDuration');
const inspectStageBtn = document.getElementById('inspectStageBtn');
const downloadVideoBtn = document.getElementById('downloadVideoBtn');

// DOM Elements: Custom Player Controls
const playPauseBtn = document.getElementById('playPauseBtn');
const currentTimecode = document.getElementById('currentTimecode');
const totalTimecode = document.getElementById('totalTimecode');
const scrubberTrackContainer = document.getElementById('scrubberTrackContainer');
const playerProgressFill = document.getElementById('playerProgressFill');
const volumeToggleBtn = document.getElementById('volumeToggleBtn');
const loopToggleBtn = document.getElementById('loopToggleBtn');
const fullscreenBtn = document.getElementById('fullscreenBtn');

// DOM Elements: Telemetry & Terminal Panel
const studioTabs = document.querySelectorAll('.studio-tab');
const tabContentLogs = document.getElementById('tabContentLogs');
const tabContentTelemetry = document.getElementById('tabContentTelemetry');
const tabContentStoryboard = document.getElementById('tabContentStoryboard');
const renderStatusBadge = document.getElementById('renderStatusBadge');
const renderProgressBar = document.getElementById('renderProgressBar');
const clearLogsBtn = document.getElementById('clearLogsBtn');
const telemetryFps = document.getElementById('telemetryFps');
const telemetryFrames = document.getElementById('telemetryFrames');
const telemetryPercent = document.getElementById('telemetryPercent');
const telemetryEta = document.getElementById('telemetryEta');
const telemetryAudio = document.getElementById('telemetryAudio');
const storyboardJsonView = document.getElementById('storyboardJsonView');
const copyJsonBtn = document.getElementById('copyJsonBtn');

// DOM Elements: Media Vault Modal
const vaultModal = document.getElementById('vaultModal');
const closeVaultBtn = document.getElementById('closeVaultBtn');
const vaultGrid = document.getElementById('vaultGrid');
const vaultSearchInput = document.getElementById('vaultSearchInput');

// Archetype Definitions for Dynamic Shot Creation
const ARCHETYPES = [
  { id: 'kinetic_manifesto', label: 'Kinetic Manifesto', desc: 'Bold kinetic wordmark reveal & manifesto statement' },
  { id: 'product_showcase', label: 'Product 3D Showcase', desc: 'Hardware elevation, titanium finish & turntable' },
  { id: 'terminal_code_stream', label: 'Terminal Code Stream', desc: 'Live hacker terminal, syntax typing stream & status' },
  { id: 'financial_telemetry', label: 'Financial Telemetry', desc: 'Candlestick trading chart, volume bars & live ticker' },
  { id: 'split_comparison', label: 'Split Comparison', desc: 'Before vs After interactive split comparison panel' },
  { id: 'bento_grid_v2', label: 'Bento Grid v2', desc: 'Asymmetric feature bento grid with live metrics' },
  { id: 'metric_impact_matrix', label: 'Metric Impact Matrix', desc: 'High-density KPI statistics with sparklines' },
  { id: 'brand_stinger_outro', label: 'Brand Stinger Outro', desc: 'Cinema logo resolve, audio sting & web callout' },
  { id: 'editorial_lookbook', label: 'Editorial Lookbook', desc: 'High-fashion typographic luxury spread' },
  { id: 'coin_parade', label: 'Token Coin Parade', desc: '3D floating isometric tokens & crypto parade' },
  { id: 'blueprint_reveal', label: 'Blueprint Wireframe', desc: 'CAD architectural schematic with floating cursor' },
  { id: 'dashboard_device', label: 'Device Mockup', desc: 'Mobile/Desktop device frame with UI preview' },
  { id: 'kinetic_parallax', label: 'Spatial Parallax', desc: 'Multi-plane spatial floating parallax cloud' },
  { id: 'cinematic_hero', label: 'Cinematic Hero', desc: 'High-contrast cinematic widescreen hero title' }
];

// Cinema Transition Types
const TRANSITIONS = [
  { id: 'whip_pan_left', label: 'Whip Pan Left' },
  { id: 'zoom_punch', label: 'Zoom Punch' },
  { id: 'rotational_snap_3d', label: '3D Snap Perspective' },
  { id: 'whip_pan_right', label: 'Whip Pan Right' },
  { id: 'shutter_split', label: 'Dual Shutter Split' },
  { id: 'circular_iris', label: 'Cinema Iris Aperture' },
  { id: 'depth_dissolve', label: 'Depth Dissolve' },
  { id: 'whip_pan_up', label: 'Whip Pan Up' }
];

// Themes
const BG_THEMES = [
  { id: 'dark_grid', label: 'Dark Grid' },
  { id: 'carbon_grid', label: 'Carbon Grid' },
  { id: 'cream_grid', label: 'Cream Grid' },
  { id: 'lime_grid', label: 'Lime Grid' },
  { id: 'matrix_mono', label: 'Matrix Monochrome' },
  { id: 'deep_space', label: 'Deep Space' }
];

// -------------------------------------------------------------
// INITIALIZATION
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  refreshLucide();
  checkSystemStatus();
  loadPresets();
  loadVaultVideos();
  setupEventListeners();
  updateStageAspectRatio(aspectRatioSelect.value);
});

function refreshLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

function formatTime(seconds) {
  const s = Math.max(0, seconds || 0);
  const mins = Math.floor(s / 60);
  const secs = Math.floor(s % 60);
  const ms = Math.floor((s % 1) * 100);
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
}

function logToTerminal(msg, level = 'info') {
  const line = document.createElement('div');
  line.className = 'leading-relaxed break-all';
  
  const timestamp = document.createElement('span');
  timestamp.className = 'text-zinc-600 font-mono';
  timestamp.textContent = `[${new Date().toLocaleTimeString()}] `;
  
  const text = document.createElement('span');
  if (level === 'error') text.className = 'text-red-400';
  else if (level === 'success') text.className = 'text-sageMuted';
  else if (level === 'warn') text.className = 'text-bronzeMuted';
  else text.className = 'text-zinc-300';
  text.textContent = String(msg ?? '');
  
  line.appendChild(timestamp);
  line.appendChild(text);
  tabContentLogs.appendChild(line);
  tabContentLogs.scrollTop = tabContentLogs.scrollHeight;
}

// -------------------------------------------------------------
// EVENT LISTENERS SETUP
// -------------------------------------------------------------
function setupEventListeners() {
  // Prompt Chips
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      promptInput.value = chip.getAttribute('data-prompt');
      promptInput.focus();
    });
  });

  // Aspect Ratio & Layout
  aspectRatioSelect.addEventListener('change', (e) => {
    updateStageAspectRatio(e.target.value);
    if (currentStoryboard) {
      currentStoryboard.aspect_ratio = e.target.value;
      syncStoryboardJson();
    }
  });

  // Engine Selector
  engineSelect.addEventListener('change', (e) => {
    const mode = e.target.value;
    if (mode === 'chromium') {
      activeEngineLabel.textContent = 'Chromium Motion Graphics';
      engineDescription.textContent = 'Broadcast-grade HTML5/CSS3 motion graphics compiled via Chromium headless browser. Dual-scene simultaneous handovers, spring physics, and procedural audio synthesis.';
      engineBadgeInfo.textContent = '1080p Broadcast';
      footerEstTime.textContent = 'Est: ~4-8s';
    } else if (mode === 'comfyui') {
      activeEngineLabel.textContent = 'ComfyUI Generative Diffusion';
      engineDescription.textContent = 'Neural generative text-to-video diffusion models running locally via ComfyUI. Generates physical video footage from shot prompts.';
      engineBadgeInfo.textContent = 'Neural Diffusion';
      footerEstTime.textContent = 'Est: ~30-60s';
    } else {
      activeEngineLabel.textContent = 'OpenCV Procedural Matrix';
      engineDescription.textContent = 'High-velocity CPU/GPU pixel drawing engine via OpenCV and NumPy raster buffers.';
      engineBadgeInfo.textContent = 'Procedural Matrix';
      footerEstTime.textContent = 'Est: ~1-3s';
    }
  });

  // Presets & Buttons
  presetSelect.addEventListener('change', handlePresetChange);
  generateStoryboardBtn.addEventListener('click', handleGenerateStoryboard);
  startRenderBtn.addEventListener('click', handleStartRender);
  addSceneBtn.addEventListener('click', handleAddScene);
  clearScenesBtn.addEventListener('click', handleClearScenes);

  // Vault Modal
  toggleVaultBtn.addEventListener('click', () => {
    vaultModal.classList.remove('hidden');
    loadVaultVideos();
  });
  closeVaultBtn.addEventListener('click', () => vaultModal.classList.add('hidden'));
  vaultModal.addEventListener('click', (e) => {
    if (e.target === vaultModal) vaultModal.classList.add('hidden');
  });
  vaultSearchInput.addEventListener('input', handleVaultSearch);

  // Studio Tabs
  studioTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      studioTabs.forEach(t => {
        t.classList.remove('active', 'text-zinc-300', 'border-zinc-200');
        t.classList.add('text-zinc-500', 'border-transparent');
      });
      tab.classList.add('active', 'text-zinc-300', 'border-zinc-200');
      tab.classList.remove('text-zinc-500', 'border-transparent');

      tabContentLogs.classList.add('hidden');
      tabContentTelemetry.classList.add('hidden');
      tabContentStoryboard.classList.add('hidden');

      if (target === 'logs') tabContentLogs.classList.remove('hidden');
      if (target === 'telemetry') tabContentTelemetry.classList.remove('hidden');
      if (target === 'storyboard') {
        tabContentStoryboard.classList.remove('hidden');
        syncStoryboardJson();
      }
    });
  });

  clearLogsBtn.addEventListener('click', () => {
    tabContentLogs.innerHTML = '';
    logToTerminal('Console cleared.');
  });

  copyJsonBtn.addEventListener('click', () => {
    if (!currentStoryboard) return;
    navigator.clipboard.writeText(JSON.stringify(currentStoryboard, null, 2)).then(() => {
      copyJsonBtn.textContent = 'Copied!';
      setTimeout(() => copyJsonBtn.textContent = 'Copy JSON', 1800);
    });
  });

  // Viewport Actions
  inspectStageBtn.addEventListener('click', () => {
    if (activeStageHtmlUrl) window.open(activeStageHtmlUrl, '_blank');
  });

  // Custom Video Player Controls
  setupCustomVideoPlayer();
}

function updateStageAspectRatio(aspect) {
  playerFrame.className = 'flex items-center justify-center relative rounded-lg border border-borderSubtle overflow-hidden bg-black shadow-2xl transition-all';
  if (aspect === '9:16') {
    playerFrame.classList.add('stage-9-16');
    activeVideoAspect.textContent = '9:16 Mobile';
  } else if (aspect === '1:1') {
    playerFrame.classList.add('stage-1-1');
    activeVideoAspect.textContent = '1:1 Square';
  } else if (aspect === '4:5') {
    playerFrame.classList.add('stage-4-5');
    activeVideoAspect.textContent = '4:5 Social';
  } else {
    playerFrame.classList.add('stage-16-9');
    activeVideoAspect.textContent = '16:9 Cinema';
  }
}

// -------------------------------------------------------------
// CUSTOM VIDEO PLAYER CONTROLS
// -------------------------------------------------------------
function setupCustomVideoPlayer() {
  playPauseBtn.addEventListener('click', () => {
    if (masterVideoPlayer.paused || masterVideoPlayer.ended) {
      masterVideoPlayer.play();
    } else {
      masterVideoPlayer.pause();
    }
  });

  masterVideoPlayer.addEventListener('play', () => {
    playPauseBtn.innerHTML = '<i data-lucide="pause" class="w-4 h-4 fill-current"></i>';
    refreshLucide();
  });

  masterVideoPlayer.addEventListener('pause', () => {
    playPauseBtn.innerHTML = '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
    refreshLucide();
  });

  masterVideoPlayer.addEventListener('timeupdate', () => {
    const cur = masterVideoPlayer.currentTime;
    const dur = masterVideoPlayer.duration || 0;
    currentTimecode.textContent = formatTime(cur);
    totalTimecode.textContent = formatTime(dur);
    const pct = dur > 0 ? (cur / dur) * 100 : 0;
    playerProgressFill.style.width = `${pct}%`;
  });

  masterVideoPlayer.addEventListener('loadedmetadata', () => {
    totalTimecode.textContent = formatTime(masterVideoPlayer.duration);
    activeVideoDuration.textContent = `${masterVideoPlayer.duration.toFixed(1)}s`;
  });

  scrubberTrackContainer.addEventListener('click', (e) => {
    const rect = scrubberTrackContainer.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const dur = masterVideoPlayer.duration;
    if (dur) {
      masterVideoPlayer.currentTime = pos * dur;
    }
  });

  volumeToggleBtn.addEventListener('click', () => {
    masterVideoPlayer.muted = !masterVideoPlayer.muted;
    if (masterVideoPlayer.muted) {
      volumeToggleBtn.innerHTML = '<i data-lucide="volume-x" class="w-4 h-4 text-zinc-500"></i>';
    } else {
      volumeToggleBtn.innerHTML = '<i data-lucide="volume-2" class="w-4 h-4"></i>';
    }
    refreshLucide();
  });

  loopToggleBtn.addEventListener('click', () => {
    masterVideoPlayer.loop = !masterVideoPlayer.loop;
    if (masterVideoPlayer.loop) {
      loopToggleBtn.classList.add('text-white', 'font-bold');
      loopToggleBtn.classList.remove('text-zinc-500');
    } else {
      loopToggleBtn.classList.remove('text-white', 'font-bold');
      loopToggleBtn.classList.add('text-zinc-500');
    }
  });

  fullscreenBtn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      if (playerFrame.requestFullscreen) playerFrame.requestFullscreen();
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  });
}

// -------------------------------------------------------------
// SYSTEM STATUS CHECK
// -------------------------------------------------------------
async function checkSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.storyboard_ai_configured) {
      directorStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-sageMuted';
      directorStatusText.textContent = `Director Ready (${data.storyboard_model || 'gpt-oss-120b'})`;
    } else {
      directorStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-brickMuted';
      directorStatusText.textContent = 'Director Key Missing';
    }
  } catch (err) {
    directorStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-brickMuted';
    directorStatusText.textContent = 'Backend Offline';
  }
}

// -------------------------------------------------------------
// PRESETS
// -------------------------------------------------------------
async function loadPresets() {
  try {
    const res = await fetch('/api/presets');
    const data = await res.json();
    presetSelect.innerHTML = '<option value="">Load Film Preset...</option>';
    (data.presets || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = `${p.title} (${p.aspect_ratio}, ${p.duration}s)`;
      opt.dataset.storyboard = JSON.stringify(p.storyboard);
      presetSelect.appendChild(opt);
    });
  } catch (err) {
    console.error('Error loading presets:', err);
  }
}

function handlePresetChange() {
  const selectedOpt = presetSelect.options[presetSelect.selectedIndex];
  if (!selectedOpt || !selectedOpt.dataset.storyboard) return;

  try {
    const sb = JSON.parse(selectedOpt.dataset.storyboard);
    currentStoryboard = sb;
    aspectRatioSelect.value = sb.aspect_ratio || '16:9';
    updateStageAspectRatio(sb.aspect_ratio || '16:9');
    moodSelect.value = sb.mood || 'cinematic_tech';
    renderSceneCards();
    startRenderBtn.disabled = false;
    syncStoryboardJson();
    logToTerminal(`Preset loaded: "${sb.title}" with ${sb.scenes.length} production shots.`, 'success');
  } catch (err) {
    console.error('Invalid preset data:', err);
  }
}

// -------------------------------------------------------------
// GROQ AI STORYBOARD GENERATION
// -------------------------------------------------------------
async function handleGenerateStoryboard() {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    alert('Please enter a creative video prompt or click one of the quick suggestions.');
    promptInput.focus();
    return;
  }

  generateStoryboardBtn.disabled = true;
  generateStoryboardBtn.innerHTML = `
    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-obsidian inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>AI Director Composing Storyboard...</span>
  `;

  renderStatusBadge.textContent = 'AI DIRECTING';
  renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700';
  logToTerminal(`Sending creative brief to Groq AI Director: "${prompt}"`);

  try {
    const res = await fetch('/api/storyboard/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt,
        aspect_ratio: aspectRatioSelect.value,
        target_duration: parseFloat(durationSelect.value),
        mood: moodSelect.value
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Storyboard request failed (HTTP ${res.status})`);
    if (data.success && data.storyboard) {
      currentStoryboard = data.storyboard;
      
      // Auto-assign Archetypes and Transitions intelligently if not already present
      currentStoryboard.scenes.forEach((sc, idx) => {
        if (!sc.layout && !sc.type) {
          sc.type = ARCHETYPES[idx % ARCHETYPES.length].id;
        }
        if (!sc.transition_out) {
          sc.transition_out = TRANSITIONS[idx % TRANSITIONS.length].id;
        }
        if (!sc.bg_theme) {
          sc.bg_theme = 'dark_grid';
        }
      });

      renderSceneCards();
      startRenderBtn.disabled = false;
      syncStoryboardJson();
      renderStatusBadge.textContent = 'STORYBOARD READY';
      renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-sageMuted';
      logToTerminal(`AI Creative Director produced "${currentStoryboard.title}" (${currentStoryboard.scenes.length} shots, ${currentStoryboard.genre || 'Cinematic'}).`, 'success');
    } else {
      throw new Error(data.detail || 'Could not generate storyboard');
    }
  } catch (err) {
    console.error('Error generating storyboard:', err);
    logToTerminal(`Director error: ${err.message}`, 'error');
    renderStatusBadge.textContent = 'DIRECTOR FAILED';
    renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-800';
    alert('AI Director Error: ' + err.message);
  } finally {
    generateStoryboardBtn.disabled = false;
    generateStoryboardBtn.innerHTML = `
      <i data-lucide="wand-2" class="w-4 h-4"></i>
      <span>Generate Storyboard (Groq Director)</span>
    `;
    refreshLucide();
  }
}

// -------------------------------------------------------------
// INTERACTIVE SHOT TIMELINE & SCENE CARDS
// -------------------------------------------------------------
function renderSceneCards() {
  if (!currentStoryboard || !currentStoryboard.scenes || !currentStoryboard.scenes.length) {
    scenesContainer.innerHTML = `
      <div class="p-6 rounded-lg border border-dashed border-zinc-800 text-center text-xs text-zinc-500 space-y-2">
        <i data-lucide="film" class="w-6 h-6 mx-auto text-zinc-600"></i>
        <p>No shots loaded. Enter a creative prompt above and click "Generate Storyboard" or load a showcase preset.</p>
      </div>
    `;
    sceneCount.textContent = '0';
    timelineStatsBadge.textContent = '0 shots · 0.0s';
    refreshLucide();
    return;
  }

  const scenes = currentStoryboard.scenes;
  const totalDur = scenes.reduce((sum, s) => sum + (parseFloat(s.duration) || 3.0), 0);
  sceneCount.textContent = scenes.length;
  timelineStatsBadge.textContent = `${scenes.length} shots · ${totalDur.toFixed(1)}s total`;

  scenesContainer.innerHTML = '';

  scenes.forEach((sc, idx) => {
    const card = document.createElement('div');
    card.className = 'scene-card space-y-2.5';
    card.dataset.idx = idx;

    // Archetype selection
    const currentArchetype = sc.layout || sc.type || 'kinetic_manifesto';
    const currentTransition = sc.transition_out || 'whip_pan_left';
    const currentTheme = sc.bg_theme || 'dark_grid';

    card.innerHTML = `
      <!-- Card Header: Shot Number + Controls -->
      <div class="flex items-center justify-between border-b border-borderSubtle pb-2">
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300">
            SHOT ${String(idx + 1).padStart(2, '0')}
          </span>
          <span class="text-[10px] font-mono text-zinc-500">
            ${sc.camera || 'Cinematic Angle'}
          </span>
        </div>

        <div class="flex items-center gap-1.5">
          <!-- Duration -->
          <div class="flex items-center gap-1">
            <input type="number" step="0.5" min="1" max="20" value="${escapeHtml(sc.duration || 3.5)}" class="scene-duration-input w-12 bg-obsidian border border-borderSubtle text-[11px] text-zinc-200 rounded px-1.5 py-0.5 text-center font-mono" data-idx="${idx}">
            <span class="text-[10px] font-mono text-zinc-500">s</span>
          </div>

          <!-- Reorder & Action Buttons -->
          <button class="move-up-btn text-zinc-500 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800 transition-colors" data-idx="${idx}" title="Move Up" ${idx === 0 ? 'disabled style="opacity:0.3"' : ''}>
            <i data-lucide="chevron-up" class="w-3.5 h-3.5"></i>
          </button>
          <button class="move-down-btn text-zinc-500 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800 transition-colors" data-idx="${idx}" title="Move Down" ${idx === scenes.length - 1 ? 'disabled style="opacity:0.3"' : ''}>
            <i data-lucide="chevron-down" class="w-3.5 h-3.5"></i>
          </button>
          <button class="duplicate-scene-btn text-zinc-500 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800 transition-colors" data-idx="${idx}" title="Duplicate Shot">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
          </button>
          <button class="delete-scene-btn text-zinc-500 hover:text-red-400 p-1 rounded hover:bg-zinc-800 transition-colors" data-idx="${idx}" title="Delete Shot">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      <!-- Archetype & Cinema Transition Pickers -->
      <div class="grid grid-cols-3 gap-1.5">
        <div class="space-y-0.5">
          <label class="text-[9px] font-mono text-zinc-500 uppercase">Archetype</label>
          <select class="scene-archetype-select w-full bg-obsidian border border-borderSubtle text-[10px] text-zinc-300 rounded px-1.5 py-1 outline-none" data-idx="${idx}">
            ${ARCHETYPES.map(a => `<option value="${a.id}" ${currentArchetype === a.id ? 'selected' : ''}>${a.label}</option>`).join('')}
          </select>
        </div>

        <div class="space-y-0.5">
          <label class="text-[9px] font-mono text-zinc-500 uppercase">Transition Out</label>
          <select class="scene-transition-select w-full bg-obsidian border border-borderSubtle text-[10px] text-zinc-300 rounded px-1.5 py-1 outline-none" data-idx="${idx}">
            ${TRANSITIONS.map(t => `<option value="${t.id}" ${currentTransition === t.id ? 'selected' : ''}>${t.label}</option>`).join('')}
          </select>
        </div>

        <div class="space-y-0.5">
          <label class="text-[9px] font-mono text-zinc-500 uppercase">Atmosphere</label>
          <select class="scene-theme-select w-full bg-obsidian border border-borderSubtle text-[10px] text-zinc-300 rounded px-1.5 py-1 outline-none" data-idx="${idx}">
            ${BG_THEMES.map(th => `<option value="${th.id}" ${currentTheme === th.id ? 'selected' : ''}>${th.label}</option>`).join('')}
          </select>
        </div>
      </div>

      <!-- Text Inputs: Badge & Headline -->
      <div class="space-y-1.5 pt-0.5">
        <div class="grid grid-cols-3 gap-1.5">
          <input type="text" placeholder="Badge (01 // CHAPTER)" value="${escapeHtml(sc.badge || `0${idx + 1} // ${currentArchetype.toUpperCase()}`)}" class="scene-badge-input bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-400 rounded px-2 py-1 outline-none" data-idx="${idx}">
          <input type="text" placeholder="Headline / Title" value="${escapeHtml(sc.headline || sc.brand_title || '')}" class="scene-headline-input col-span-2 bg-obsidian border border-borderSubtle text-xs font-semibold text-zinc-200 rounded px-2 py-1 outline-none" data-idx="${idx}">
        </div>
        <input type="text" placeholder="Subtext / Tagline / Editorial note" value="${escapeHtml(sc.subtext || sc.tagline || '')}" class="scene-subtext-input w-full bg-obsidian border border-borderSubtle text-[11px] text-zinc-400 rounded px-2 py-1 outline-none" data-idx="${idx}">
      </div>

      <!-- Archetype Specific Custom Fields -->
      ${renderArchetypeFields(sc, idx)}

      <!-- Standalone Footage Prompt (Used for ComfyUI and Reference Framing) -->
      <div class="space-y-0.5 pt-1">
        <label class="text-[9px] font-mono text-zinc-500 uppercase flex items-center justify-between">
          <span>Camera & Footage Directive</span>
          <span>${sc.lighting || 'Cinematic Lighting'}</span>
        </label>
        <textarea rows="2" placeholder="Shot description: subjects, camera lens, movement, lighting atmosphere..." class="scene-prompt-input w-full bg-obsidian border border-borderSubtle text-[10px] text-zinc-300 rounded p-1.5 outline-none font-sans resize-none" data-idx="${idx}">${escapeHtml(sc.video_prompt || sc.shot_prompt || '')}</textarea>
      </div>
    `;

    scenesContainer.appendChild(card);
  });

  attachSceneListeners();
  refreshLucide();
}

function renderArchetypeFields(sc, idx) {
  const type = sc.layout || sc.type || '';

  if (type === 'terminal_code_stream') {
    return `
      <div class="p-2 rounded bg-zinc-950/80 border border-borderSubtle space-y-1.5">
        <div class="flex items-center justify-between">
          <input type="text" placeholder="Filename (e.g. engine.ts)" value="${escapeHtml(sc.filename || 'runtime.ts')}" class="scene-filename-input w-40 bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-300 rounded px-1.5 py-0.5" data-idx="${idx}">
          <span class="text-[9px] font-mono text-zinc-500">TypeScript / CLI</span>
        </div>
        <textarea rows="2" placeholder="Code lines (one per line)" class="scene-code-input w-full bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-300 rounded p-1.5 resize-none" data-idx="${idx}">${escapeHtml((sc.code_lines || ['const engine = new CineMatrix();', 'await engine.render({ resolution: "1080p" });']).join('\n'))}</textarea>
      </div>
    `;
  }

  if (type === 'financial_telemetry') {
    return `
      <div class="p-2 rounded bg-zinc-950/80 border border-borderSubtle grid grid-cols-3 gap-1.5">
        <input type="text" placeholder="Ticker (BTC/USD)" value="${escapeHtml(sc.ticker || '$AXIOM')}" class="scene-ticker-input bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-300 rounded px-1.5 py-0.5" data-idx="${idx}">
        <input type="text" placeholder="Price ($94,820)" value="${escapeHtml(sc.price || '$148.92')}" class="scene-price-input bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-300 rounded px-1.5 py-0.5" data-idx="${idx}">
        <input type="text" placeholder="Delta (+28.4%)" value="${escapeHtml(sc.delta || '+34.2%')}" class="scene-delta-input bg-obsidian border border-borderSubtle text-[10px] font-mono text-sageMuted rounded px-1.5 py-0.5" data-idx="${idx}">
      </div>
    `;
  }

  if (type === 'split_comparison') {
    return `
      <div class="p-2 rounded bg-zinc-950/80 border border-borderSubtle grid grid-cols-2 gap-1.5">
        <input type="text" placeholder="Left State (Legacy / Before)" value="${escapeHtml(sc.left_label || 'Legacy Pipelines')}" class="scene-left-input bg-obsidian border border-borderSubtle text-[10px] text-zinc-400 rounded px-1.5 py-0.5" data-idx="${idx}">
        <input type="text" placeholder="Right State (CineMatrix / After)" value="${escapeHtml(sc.right_label || 'Autonomous Studio')}" class="scene-right-input bg-obsidian border border-borderSubtle text-[10px] text-zinc-200 rounded px-1.5 py-0.5" data-idx="${idx}">
      </div>
    `;
  }

  if (type === 'bento_grid_v2' || type === 'blueprint_reveal') {
    return `
      <div class="p-2 rounded bg-zinc-950/80 border border-borderSubtle space-y-1">
        <input type="text" placeholder="Pills / Feature Tags (comma separated)" value="${escapeHtml((sc.pills || ['Ultra-low Latency', 'Zero AI Slop', '1080p Master']).join(', '))}" class="scene-pills-input w-full bg-obsidian border border-borderSubtle text-[10px] text-zinc-300 rounded px-1.5 py-0.5" data-idx="${idx}">
      </div>
    `;
  }

  if (type === 'brand_stinger_outro') {
    return `
      <div class="p-2 rounded bg-zinc-950/80 border border-borderSubtle grid grid-cols-2 gap-1.5">
        <input type="text" placeholder="Brand Name" value="${escapeHtml(sc.brand_name || sc.brand_title || currentStoryboard.title || 'CineMatrix')}" class="scene-brand-input bg-obsidian border border-borderSubtle text-[10px] text-zinc-200 rounded px-1.5 py-0.5" data-idx="${idx}">
        <input type="text" placeholder="Web URL / Handle" value="${escapeHtml(sc.web_url || 'cinematrix.ai')}" class="scene-url-input bg-obsidian border border-borderSubtle text-[10px] font-mono text-zinc-400 rounded px-1.5 py-0.5" data-idx="${idx}">
      </div>
    `;
  }

  return '';
}

function attachSceneListeners() {
  document.querySelectorAll('.scene-archetype-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].type = e.target.value;
      currentStoryboard.scenes[idx].layout = e.target.value;
      renderSceneCards();
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-transition-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].transition_out = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-theme-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].bg_theme = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-duration-input').forEach(inp => {
    inp.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].duration = parseFloat(e.target.value) || 3.0;
      updateTimelineStats();
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-badge-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].badge = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-headline-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].headline = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-subtext-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].subtext = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-prompt-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].video_prompt = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-filename-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].filename = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-code-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].code_lines = e.target.value.split('\n');
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-ticker-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].ticker = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-price-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].price = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-delta-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].delta = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-left-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].left_label = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-right-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].right_label = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-pills-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].pills = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-brand-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].brand_name = e.target.value;
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.scene-url-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].web_url = e.target.value;
      syncStoryboardJson();
    });
  });

  // Reordering & Actions
  document.querySelectorAll('.move-up-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(btn.dataset.idx);
      if (idx > 0) {
        const item = currentStoryboard.scenes.splice(idx, 1)[0];
        currentStoryboard.scenes.splice(idx - 1, 0, item);
        renderSceneCards();
        syncStoryboardJson();
      }
    });
  });

  document.querySelectorAll('.move-down-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(btn.dataset.idx);
      if (idx < currentStoryboard.scenes.length - 1) {
        const item = currentStoryboard.scenes.splice(idx, 1)[0];
        currentStoryboard.scenes.splice(idx + 1, 0, item);
        renderSceneCards();
        syncStoryboardJson();
      }
    });
  });

  document.querySelectorAll('.duplicate-scene-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(btn.dataset.idx);
      const clone = JSON.parse(JSON.stringify(currentStoryboard.scenes[idx]));
      clone.badge = `0${currentStoryboard.scenes.length + 1} // COPY`;
      currentStoryboard.scenes.splice(idx + 1, 0, clone);
      renderSceneCards();
      syncStoryboardJson();
    });
  });

  document.querySelectorAll('.delete-scene-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(btn.dataset.idx);
      currentStoryboard.scenes.splice(idx, 1);
      renderSceneCards();
      syncStoryboardJson();
      if (!currentStoryboard.scenes.length) startRenderBtn.disabled = true;
    });
  });
}

function updateTimelineStats() {
  if (!currentStoryboard || !currentStoryboard.scenes) return;
  const totalDur = currentStoryboard.scenes.reduce((sum, s) => sum + (parseFloat(s.duration) || 3.0), 0);
  timelineStatsBadge.textContent = `${currentStoryboard.scenes.length} shots · ${totalDur.toFixed(1)}s total`;
}

function syncStoryboardJson() {
  if (currentStoryboard) {
    storyboardJsonView.textContent = JSON.stringify(currentStoryboard, null, 2);
  }
}

function handleAddScene() {
  if (!currentStoryboard) {
    currentStoryboard = {
      title: "Master Campaign Film",
      aspect_ratio: aspectRatioSelect.value,
      fps: parseInt(fpsSelect.value) || 24,
      mood: moodSelect.value,
      scenes: []
    };
  }

  const nextIdx = currentStoryboard.scenes.length;
  const archetypesList = ['kinetic_manifesto', 'terminal_code_stream', 'product_showcase', 'financial_telemetry', 'split_comparison', 'bento_grid_v2', 'metric_impact_matrix', 'brand_stinger_outro'];
  const assignedArchetype = archetypesList[nextIdx % archetypesList.length];

  currentStoryboard.scenes.push({
    type: assignedArchetype,
    layout: assignedArchetype,
    duration: 3.5,
    bg_theme: "dark_grid",
    transition_out: TRANSITIONS[nextIdx % TRANSITIONS.length].id,
    badge: `0${nextIdx + 1} // ${assignedArchetype.toUpperCase()}`,
    headline: "Engineered for Velocity",
    subtext: "Precision programmatic media generation",
    video_prompt: "High-definition technical cinema shot, crisp dynamic motion, subtle camera push, clean lighting"
  });

  renderSceneCards();
  startRenderBtn.disabled = false;
  syncStoryboardJson();
  logToTerminal(`Added shot ${currentStoryboard.scenes.length} (${assignedArchetype}).`);
}

function handleClearScenes() {
  if (!currentStoryboard || !currentStoryboard.scenes.length) return;
  if (confirm('Clear all shots from timeline?')) {
    currentStoryboard.scenes = [];
    renderSceneCards();
    startRenderBtn.disabled = true;
    syncStoryboardJson();
    logToTerminal('All shots cleared.');
  }
}

// -------------------------------------------------------------
// VIDEO RENDERING PIPELINE & PROGRESS TRACKING
// -------------------------------------------------------------
async function handleStartRender() {
  if (!currentStoryboard || !currentStoryboard.scenes.length) {
    alert('Please compose or load a storyboard first.');
    return;
  }

  currentStoryboard.aspect_ratio = aspectRatioSelect.value;
  currentStoryboard.mood = moodSelect.value;
  currentStoryboard.fps = parseInt(fpsSelect.value) || 24;

  const selectedEngine = engineSelect ? engineSelect.value : 'chromium';

  startRenderBtn.disabled = true;
  startRenderBtn.innerHTML = `
    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-obsidian inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>Rendering Master Video (${selectedEngine.toUpperCase()})...</span>
  `;

  renderStatusBadge.textContent = 'DISPATCHING';
  renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700';

  const engineLabel = selectedEngine === 'comfyui' ? 'ComfyUI Generative Diffusion' : selectedEngine === 'opencv' ? 'OpenCV Pixel Engine' : 'Chromium HTML5 Motion Cinema';
  logToTerminal(`Dispatching render job to ${engineLabel} (${currentStoryboard.scenes.length} shots, 1080p)...`);

  try {
    const res = await fetch('/api/render', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        storyboard: currentStoryboard,
        engine: selectedEngine
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Render failed with HTTP ${res.status}`);
    if (!data.job_id) throw new Error('API returned no job ID');

    activeJobId = data.job_id;
    pollRenderProgress();
  } catch (err) {
    console.error('Error starting render:', err);
    logToTerminal(`Render failed: ${err.message}`, 'error');
    alert('Render Error: ' + err.message);
    resetRenderBtn();
  }
}

function pollRenderProgress() {
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(async () => {
    if (!activeJobId) {
      clearInterval(pollTimer);
      return;
    }

    try {
      const res = await fetch(`/api/render/progress/${activeJobId}`);
      const job = await res.json();

      // Telemetry updates
      renderProgressBar.style.width = `${job.percent || 0}%`;
      telemetryFps.textContent = job.fps ? `${job.fps} fps` : '--';
      telemetryFrames.textContent = job.frame ? `${job.frame} / ${job.total_frames}` : '-- / --';
      telemetryPercent.textContent = `${job.percent || 0}%`;
      telemetryEta.textContent = job.eta_seconds ? `${job.eta_seconds}s` : '--';

      if (job.message && job.message !== lastLoggedJobMessage) {
        logToTerminal(job.message);
        lastLoggedJobMessage = job.message;
      }

      if (job.status === 'processing') {
        renderStatusBadge.textContent = `RENDERING ${job.percent || 0}%`;
        renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-bronzeMuted';
      } else if (job.status === 'completed') {
        clearInterval(pollTimer);
        handleRenderCompleted(job);
      } else if (job.status === 'failed') {
        clearInterval(pollTimer);
        logToTerminal(`ERROR: ${job.error || 'Generation failed.'}`, 'error');
        renderStatusBadge.textContent = 'FAILED';
        renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-800';
        resetRenderBtn();
      }
    } catch (err) {
      console.error('Progress polling error:', err);
    }
  }, 900);
}

function handleRenderCompleted(job) {
  renderStatusBadge.textContent = 'MASTER DELIVERED';
  renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-sageMuted';
  renderProgressBar.style.width = '100%';

  const res = job.result || {};
  const sizeMB = res.file_size_bytes ? (res.file_size_bytes / 1024 / 1024).toFixed(2) : '--';
  logToTerminal(`Master Film Delivered: ${job.video_url} (${sizeMB} MB, ${res.duration}s in ${res.render_time_seconds}s)`, 'success');
  if (res.audio_status) logToTerminal(res.audio_status, 'success');

  // Load into player stage
  videoSource.src = job.video_url;
  masterVideoPlayer.load();
  emptyPlayerState.classList.add('hidden');
  masterVideoPlayer.play().catch(() => {});

  // Update Metadata Bar
  activeVideoTitle.textContent = res.title || currentStoryboard.title || 'Master Video';
  activeVideoAspect.textContent = res.aspect_ratio || currentStoryboard.aspect_ratio || '16:9 Cinema';
  activeVideoDuration.textContent = `${res.duration || '--'}s`;

  // Enable download button
  downloadVideoBtn.href = job.video_url;
  downloadVideoBtn.setAttribute('download', `${job.video_id}.mp4`);
  downloadVideoBtn.classList.remove('pointer-events-none', 'opacity-40');

  // Stage HTML Inspection
  if (res.stage_html) {
    activeStageHtmlUrl = '/output/' + res.stage_html.split(/[\\/]/).pop();
    inspectStageBtn.classList.remove('hidden');
    inspectStageBtn.classList.add('flex');
  }

  resetRenderBtn();
  loadVaultVideos();
}

function resetRenderBtn() {
  startRenderBtn.disabled = false;
  startRenderBtn.innerHTML = `
    <i data-lucide="play" class="w-4 h-4 fill-current"></i>
    <span>Render Master Video</span>
  `;
  refreshLucide();
}

// -------------------------------------------------------------
// MEDIA VAULT
// -------------------------------------------------------------
async function loadVaultVideos() {
  try {
    const res = await fetch('/api/videos');
    const data = await res.json();
    vaultVideosCache = data.videos || [];
    vaultCount.textContent = vaultVideosCache.length;
    renderVaultGrid(vaultVideosCache);
  } catch (err) {
    console.error('Error loading media vault:', err);
  }
}

function handleVaultSearch(e) {
  const query = (e.target.value || '').toLowerCase().trim();
  if (!query) {
    renderVaultGrid(vaultVideosCache);
    return;
  }
  const filtered = vaultVideosCache.filter(v => v.filename.toLowerCase().includes(query) || v.created_at.includes(query));
  renderVaultGrid(filtered);
}

function renderVaultGrid(videos) {
  if (!videos.length) {
    vaultGrid.innerHTML = `
      <div class="col-span-full py-12 text-center text-xs text-zinc-500 space-y-2">
        <i data-lucide="film" class="w-8 h-8 mx-auto text-zinc-600"></i>
        <p>No master videos match your filter.</p>
      </div>
    `;
    refreshLucide();
    return;
  }

  vaultGrid.innerHTML = '';
  videos.forEach(v => {
    const card = document.createElement('div');
    card.className = 'bg-obsidian border border-borderSubtle rounded-lg overflow-hidden group hover:border-zinc-700 transition-all flex flex-col justify-between';
    
    card.innerHTML = `
      <div class="aspect-video bg-zinc-950 relative flex items-center justify-center overflow-hidden cursor-pointer play-trigger">
        ${v.thumb_url ? `<img src="${escapeHtml(v.thumb_url)}" class="w-full h-full object-cover" alt="">` : `<i data-lucide="film" class="w-8 h-8 text-zinc-700"></i>`}
        <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all">
          <span class="w-9 h-9 rounded-full bg-white text-obsidian flex items-center justify-center">
            <i data-lucide="play" class="w-4 h-4 fill-current ml-0.5"></i>
          </span>
        </div>
      </div>

      <div class="p-3 space-y-2">
        <div class="flex items-start justify-between gap-1">
          <p class="text-xs font-semibold text-zinc-200 truncate flex-1" title="${escapeHtml(v.filename)}">${escapeHtml(v.filename)}</p>
          <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">MP4</span>
        </div>

        <div class="flex items-center justify-between text-[10px] font-mono text-zinc-500">
          <span>${escapeHtml(v.size_formatted)}</span>
          <span>${escapeHtml(v.created_at)}</span>
        </div>

        <!-- Action Row -->
        <div class="flex items-center justify-between pt-1 border-t border-borderSubtle">
          <button class="vault-play-btn text-[10px] text-zinc-300 hover:text-white flex items-center gap-1">
            <i data-lucide="play" class="w-3 h-3"></i> Play
          </button>
          <a href="${escapeHtml(v.video_url)}" download="${escapeHtml(v.filename)}" class="text-[10px] text-zinc-400 hover:text-zinc-200 flex items-center gap-1">
            <i data-lucide="download" class="w-3 h-3"></i> Save
          </a>
          <button class="vault-delete-btn text-[10px] text-zinc-500 hover:text-red-400 flex items-center gap-1" data-filename="${escapeHtml(v.filename)}">
            <i data-lucide="trash-2" class="w-3 h-3"></i> Delete
          </button>
        </div>
      </div>
    `;

    // Click to play in master viewport
    const playHandler = () => {
      videoSource.src = v.video_url;
      masterVideoPlayer.load();
      emptyPlayerState.classList.add('hidden');
      masterVideoPlayer.play().catch(() => {});

      activeVideoTitle.textContent = v.filename;
      downloadVideoBtn.href = v.video_url;
      downloadVideoBtn.setAttribute('download', v.filename);
      downloadVideoBtn.classList.remove('pointer-events-none', 'opacity-40');

      // Check for stage html
      const stageUrl = `/output/${v.id}_stage.html`;
      activeStageHtmlUrl = stageUrl;
      inspectStageBtn.classList.remove('hidden');
      inspectStageBtn.classList.add('flex');

      vaultModal.classList.add('hidden');
      logToTerminal(`Loaded video from Media Vault: ${v.filename}`);
    };

    card.querySelector('.play-trigger').addEventListener('click', playHandler);
    card.querySelector('.vault-play-btn').addEventListener('click', playHandler);

    // Delete handler
    card.querySelector('.vault-delete-btn').addEventListener('click', async (e) => {
      e.stopPropagation();
      const fn = e.currentTarget.dataset.filename;
      if (!confirm(`Are you sure you want to delete ${fn}?`)) return;
      
      try {
        const delRes = await fetch(`/api/videos/${encodeURIComponent(fn)}`, { method: 'DELETE' });
        if (delRes.ok) {
          logToTerminal(`Deleted video ${fn} from Media Vault.`, 'warn');
          loadVaultVideos();
        } else {
          alert('Could not delete video.');
        }
      } catch (err) {
        alert('Delete error: ' + err.message);
      }
    });

    vaultGrid.appendChild(card);
  });

  refreshLucide();
}
