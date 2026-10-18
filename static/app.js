// CineMatrix AI — Media Studio Application Logic

let currentStoryboard = null;
let activeJobId = null;
let pollTimer = null;
let lastLoggedJobMessage = '';

// DOM Elements
const promptInput = document.getElementById('promptInput');
const aspectRatioSelect = document.getElementById('aspectRatioSelect');
const durationSelect = document.getElementById('durationSelect');
const moodSelect = document.getElementById('moodSelect');
const generateStoryboardBtn = document.getElementById('generateStoryboardBtn');
const scenesContainer = document.getElementById('scenesContainer');
const sceneCount = document.getElementById('sceneCount');
const addSceneBtn = document.getElementById('addSceneBtn');
const startRenderBtn = document.getElementById('startRenderBtn');
const presetSelect = document.getElementById('presetSelect');

const masterVideoPlayer = document.getElementById('masterVideoPlayer');
const videoSource = document.getElementById('videoSource');
const emptyPlayerState = document.getElementById('emptyPlayerState');
const downloadVideoBtn = document.getElementById('downloadVideoBtn');
const activeVideoTitle = document.getElementById('activeVideoTitle');
const activeVideoAspect = document.getElementById('activeVideoAspect');
const activeVideoDuration = document.getElementById('activeVideoDuration');

const renderProgressBar = document.getElementById('renderProgressBar');
const renderStatusBadge = document.getElementById('renderStatusBadge');
const renderLogs = document.getElementById('renderLogs');
const telemetryFps = document.getElementById('telemetryFps');
const telemetryFrames = document.getElementById('telemetryFrames');
const telemetryEta = document.getElementById('telemetryEta');

const toggleVaultBtn = document.getElementById('toggleVaultBtn');
const vaultModal = document.getElementById('vaultModal');
const closeVaultBtn = document.getElementById('closeVaultBtn');
const vaultGrid = document.getElementById('vaultGrid');
const vaultCount = document.getElementById('vaultCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  refreshLucide();
  loadPresets();
  loadVaultVideos();

  // Setup prompt chips
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      promptInput.value = chip.getAttribute('data-prompt');
      promptInput.focus();
    });
  });

  // Setup Event Listeners
  generateStoryboardBtn.addEventListener('click', handleGenerateStoryboard);
  startRenderBtn.addEventListener('click', handleStartRender);
  addSceneBtn.addEventListener('click', handleAddScene);
  presetSelect.addEventListener('change', handlePresetChange);

  toggleVaultBtn.addEventListener('click', () => {
    vaultModal.classList.remove('hidden');
    loadVaultVideos();
  });
  closeVaultBtn.addEventListener('click', () => {
    vaultModal.classList.add('hidden');
  });
  vaultModal.addEventListener('click', (e) => {
    if (e.target === vaultModal) vaultModal.classList.add('hidden');
  });
});

function refreshLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function logToTerminal(msg) {
  const line = document.createElement('div');
  const timestamp = document.createElement('span');
  timestamp.className = 'text-zinc-600';
  timestamp.textContent = '[' + new Date().toLocaleTimeString() + '] ';
  line.appendChild(timestamp);
  line.appendChild(document.createTextNode(String(msg ?? '')));
  renderLogs.appendChild(line);
  renderLogs.scrollTop = renderLogs.scrollHeight;
}

// AI output, preset data, and user-edited text must never be interpreted as HTML.
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

// -------------------------------------------------------------
// PRESETS
// -------------------------------------------------------------
async function loadPresets() {
  try {
    const res = await fetch('/api/presets');
    const data = await res.json();
    presetSelect.innerHTML = '<option value="">Load Preset Showcase...</option>';
    data.presets.forEach(p => {
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

function handlePresetChange(e) {
  const selectedOpt = presetSelect.options[presetSelect.selectedIndex];
  if (!selectedOpt || !selectedOpt.dataset.storyboard) return;

  try {
    const sb = JSON.parse(selectedOpt.dataset.storyboard);
    currentStoryboard = sb;
    aspectRatioSelect.value = sb.aspect_ratio || '16:9';
    moodSelect.value = sb.mood || 'cinematic_tech';
    renderSceneCards();
    startRenderBtn.disabled = false;
    logToTerminal(`Preset loaded: "${sb.title}" with ${sb.scenes.length} scenes.`);
  } catch (err) {
    console.error('Invalid preset data:', err);
  }
}

// -------------------------------------------------------------
// GROQ STORYBOARD GENERATION
// -------------------------------------------------------------
async function handleGenerateStoryboard() {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    alert('Please enter a video prompt or click one of the suggestion chips.');
    promptInput.focus();
    return;
  }

  generateStoryboardBtn.disabled = true;
  generateStoryboardBtn.innerHTML = `
    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-obsidian inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>AI Director Thinking & Storyboarding...</span>
  `;

  logToTerminal(`Sending creative brief to the AI director: "${prompt}"`);

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
      renderSceneCards();
      startRenderBtn.disabled = false;
      logToTerminal(`AI creative director created "${currentStoryboard.title}" (${currentStoryboard.scenes.length} shots).`);
    } else {
      alert('Error generating storyboard: ' + (data.detail || 'Unknown error'));
    }
  } catch (err) {
    console.error('Error generating storyboard:', err);
    logToTerminal(`Storyboard generation failed: ${err.message}`);
    alert('Storyboard generation failed: ' + err.message);
  } finally {
    generateStoryboardBtn.disabled = false;
    generateStoryboardBtn.innerHTML = `
      <i data-lucide="wand-2" class="w-4 h-4"></i>
      <span>Generate Original Storyboard</span>
    `;
    refreshLucide();
  }
}

// -------------------------------------------------------------
// SCENE CARDS RENDERER & INTERACTIVE EDITOR
// -------------------------------------------------------------
function renderSceneCards() {
  if (!currentStoryboard || !currentStoryboard.scenes) {
    scenesContainer.innerHTML = `
      <div class="p-6 rounded-lg border border-dashed border-zinc-800 text-center text-xs text-zinc-500">
        No scenes active. Enter prompt or load preset.
      </div>
    `;
    sceneCount.textContent = '0';
    return;
  }

  sceneCount.textContent = currentStoryboard.scenes.length;
  scenesContainer.innerHTML = '';

  currentStoryboard.scenes.forEach((sc, idx) => {
    const card = document.createElement('div');
    card.className = 'scene-card space-y-2';

    // Type label + duration + theme + delete
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">Scene ${idx + 1}</span>
          <select class="scene-type-select bg-zinc-900 border border-borderSub text-[11px] text-zinc-300 rounded px-2 py-1 outline-none" data-idx="${idx}">
            <option value="generative_video" ${sc.type === 'generative_video' ? 'selected' : ''}>AI-Generated Footage</option>
            <option value="ui_ux_wireframe" ${sc.type === 'ui_ux_wireframe' ? 'selected' : ''}>UI/UX Wireframe</option>
            <option value="ai_neural_network" ${sc.type === 'ai_neural_network' ? 'selected' : ''}>AI Neural Network</option>
            <option value="cyber_shield" ${sc.type === 'cyber_shield' ? 'selected' : ''}>Cyber Shield</option>
            <option value="code_showcase" ${sc.type === 'code_showcase' ? 'selected' : ''}>Code Showcase</option>
            <option value="metrics_telemetry" ${sc.type === 'metrics_telemetry' ? 'selected' : ''}>Metrics Telemetry</option>
            <option value="data_analytics_chart" ${sc.type === 'data_analytics_chart' ? 'selected' : ''}>Data Chart</option>
            <option value="custom_software" ${sc.type === 'custom_software' ? 'selected' : ''}>Custom Software</option>
            <option value="brand_radar" ${sc.type === 'brand_radar' || sc.type === 'brand_stinger' ? 'selected' : ''}>Brand Radar / Stinger</option>
            <option value="kinetic_title" ${sc.type === 'kinetic_title' ? 'selected' : ''}>Kinetic Hero</option>
          </select>
          <select class="scene-theme-select bg-zinc-900 border border-borderSub text-[10px] text-zinc-400 rounded px-1.5 py-1 outline-none" data-idx="${idx}">
            <option value="dark_grid" ${sc.bg_theme === 'dark_grid' ? 'selected' : ''}>Dark Grid</option>
            <option value="cream_grid" ${sc.bg_theme === 'cream_grid' ? 'selected' : ''}>Cream Grid</option>
            <option value="lime_grid" ${sc.bg_theme === 'lime_grid' ? 'selected' : ''}>Lime Grid</option>
            <option value="carbon_grid" ${sc.bg_theme === 'carbon_grid' ? 'selected' : ''}>Carbon Grid</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <input type="number" step="0.5" min="1" max="15" value="${escapeHtml(sc.duration || 3.0)}" class="scene-duration-input w-14 bg-zinc-900 border border-borderSub text-xs text-zinc-300 rounded px-1.5 py-0.5 text-center font-mono" data-idx="${idx}">
          <span class="text-[10px] text-zinc-500">s</span>
          <button class="delete-scene-btn text-zinc-500 hover:text-zinc-300 p-1" data-idx="${idx}">✕</button>
        </div>
      </div>

      <!-- Badge & Headline -->
      <div class="space-y-1.5 pt-1">
        <input type="text" placeholder="Telemetry Badge (e.g. 01 // GENESIS)" value="${escapeHtml(sc.badge || '')}" class="scene-badge-input w-full bg-obsidian border border-borderSub text-[11px] font-mono text-zinc-400 rounded p-1.5 outline-none" data-idx="${idx}">
        <input type="text" placeholder="Scene Headline" value="${escapeHtml(sc.headline || sc.brand_title || '')}" class="scene-headline-input w-full bg-obsidian border border-borderSub text-xs font-medium text-zinc-200 rounded p-1.5 outline-none" data-idx="${idx}">
        <input type="text" placeholder="Subtext / Edit note" value="${escapeHtml(sc.subtext || sc.tagline || '')}" class="scene-subtext-input w-full bg-obsidian border border-borderSub text-[11px] text-zinc-400 rounded p-1.5 outline-none" data-idx="${idx}">
        <textarea rows="3" placeholder="Actual footage prompt: describe the subject, action, setting, composition and motion" class="scene-video-prompt-input w-full bg-obsidian border border-borderSub text-[11px] text-zinc-300 rounded p-1.5 outline-none resize-y" data-idx="${idx}">${escapeHtml(sc.video_prompt || sc.shot_prompt || '')}</textarea>
      </div>

      ${sc.chat_bubble || sc.type === 'ai_neural_network' ? `
        <div class="pt-1">
          <input type="text" placeholder="Prompt Bubble (e.g. Automate workflows)" value="${escapeHtml(sc.chat_bubble || '')}" class="scene-chat-input w-full bg-obsidian border border-borderSub text-[10px] text-zinc-300 rounded p-1.5 outline-none" data-idx="${idx}">
        </div>
      ` : ''}

      ${sc.pills || sc.type === 'ui_ux_wireframe' || sc.type === 'cyber_shield' ? `
        <div class="pt-1">
          <input type="text" placeholder="Tag Pills (comma separated)" value="${escapeHtml((sc.pills || []).join(', '))}" class="scene-pills-input w-full bg-obsidian border border-borderSub text-[10px] text-zinc-300 rounded p-1.5 outline-none" data-idx="${idx}">
        </div>
      ` : ''}

      ${sc.type === 'code_showcase' ? `
        <div class="pt-1 space-y-1">
          <input type="text" placeholder="Filename (e.g. engine.ts)" value="${escapeHtml(sc.filename || 'orchestrator.ts')}" class="scene-filename-input w-full bg-obsidian border border-borderSub text-[10px] font-mono text-zinc-400 rounded p-1" data-idx="${idx}">
          <textarea rows="2" placeholder="Code lines (one per row)" class="scene-code-input w-full bg-obsidian border border-borderSub text-[10px] font-mono text-zinc-300 rounded p-1.5 resize-none" data-idx="${idx}">${escapeHtml((sc.code_lines || []).join('\n'))}</textarea>
        </div>
      ` : ''}
    `;

    scenesContainer.appendChild(card);
  });

  // Attach Scene Input Listeners
  attachSceneListeners();
}

function attachSceneListeners() {
  document.querySelectorAll('.scene-type-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].type = e.target.value;
      renderSceneCards();
    });
  });

  document.querySelectorAll('.scene-duration-input').forEach(inp => {
    inp.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].duration = parseFloat(e.target.value) || 3.0;
    });
  });

  document.querySelectorAll('.scene-badge-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].badge = e.target.value;
    });
  });

  document.querySelectorAll('.scene-headline-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      if (currentStoryboard.scenes[idx].type === 'brand_stinger') {
        currentStoryboard.scenes[idx].brand_title = e.target.value;
      } else {
        currentStoryboard.scenes[idx].headline = e.target.value;
      }
    });
  });

  document.querySelectorAll('.scene-subtext-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      if (currentStoryboard.scenes[idx].type === 'brand_stinger') {
        currentStoryboard.scenes[idx].tagline = e.target.value;
      } else {
        currentStoryboard.scenes[idx].subtext = e.target.value;
      }
    });
  });

  document.querySelectorAll('.scene-video-prompt-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].video_prompt = e.target.value;
    });
  });

  document.querySelectorAll('.scene-filename-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].filename = e.target.value;
    });
  });

  document.querySelectorAll('.scene-code-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].code_lines = e.target.value.split('\n');
    });
  });

  document.querySelectorAll('.scene-theme-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].bg_theme = e.target.value;
    });
  });

  document.querySelectorAll('.scene-chat-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].chat_bubble = e.target.value;
    });
  });

  document.querySelectorAll('.scene-pills-input').forEach(inp => {
    inp.addEventListener('input', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes[idx].pills = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
    });
  });

  document.querySelectorAll('.delete-scene-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(e.target.dataset.idx);
      currentStoryboard.scenes.splice(idx, 1);
      renderSceneCards();
    });
  });
}

function handleAddScene() {
  if (!currentStoryboard) {
    currentStoryboard = {
      title: "Custom Film",
      aspect_ratio: aspectRatioSelect.value,
      fps: 30,
      mood: moodSelect.value,
      scenes: []
    };
  }

  currentStoryboard.scenes.push({
    type: "ui_ux_wireframe",
    duration: 3.5,
    bg_theme: "dark_grid",
    badge: `0${currentStoryboard.scenes.length + 1} // CHAPTER`,
    headline: "Engineered for Velocity",
    subtext: "Precision programmatic media generation",
    pills: ["Dynamic Flow", "Interactive UX"]
  });

  renderSceneCards();
  startRenderBtn.disabled = false;
}

// -------------------------------------------------------------
// VIDEO RENDERING PIPELINE & PROGRESS TRACKING
// -------------------------------------------------------------
async function handleStartRender() {
  if (!currentStoryboard || !currentStoryboard.scenes.length) {
    alert('Please generate or load a storyboard first.');
    return;
  }

  currentStoryboard.aspect_ratio = aspectRatioSelect.value;
  currentStoryboard.mood = moodSelect.value;

  const engineSelect = document.getElementById('engineSelect');
  const selectedEngine = engineSelect ? engineSelect.value : 'comfyui';

  startRenderBtn.disabled = true;
  startRenderBtn.innerHTML = `
    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-obsidian inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>Rendering Master Video (${selectedEngine.toUpperCase()})...</span>
  `;

  renderStatusBadge.textContent = 'RENDERING';
  renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700';

  const engineLabel = selectedEngine === 'comfyui' ? 'ComfyUI generative video model' : selectedEngine === 'opencv' ? 'OpenCV procedural graphics' : 'Chromium motion graphics';
  logToTerminal(`Dispatching render job to ${engineLabel}...`);

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
    if (!res.ok) throw new Error(data.detail || `Render request failed (HTTP ${res.status})`);
    if (!data.job_id) throw new Error('Render API did not return a job ID.');
    activeJobId = data.job_id;
    pollRenderProgress();
  } catch (err) {
    console.error('Error starting render:', err);
    logToTerminal(`Render dispatch failed: ${err.message}`);
    alert('Could not start rendering: ' + err.message);
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

      // Update Telemetry
      renderProgressBar.style.width = `${job.percent || 0}%`;
      telemetryFps.textContent = job.fps ? `${job.fps} fps` : '--';
      telemetryFrames.textContent = job.frame ? `${job.frame} / ${job.total_frames}` : '-- / --';
      telemetryEta.textContent = job.eta_seconds ? `${job.eta_seconds}s` : '--';

      if (job.message && job.message !== lastLoggedJobMessage) {
        logToTerminal(job.message);
        lastLoggedJobMessage = job.message;
      }

      if (job.status === 'completed') {
        clearInterval(pollTimer);
        handleRenderCompleted(job);
      } else if (job.status === 'failed') {
        clearInterval(pollTimer);
        logToTerminal(`ERROR: ${job.error}`);
        renderStatusBadge.textContent = 'FAILED';
        renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-800';
        resetRenderBtn();
      }
    } catch (err) {
      console.error('Progress poll error:', err);
    }
  }, 1000);
}

function handleRenderCompleted(job) {
  renderStatusBadge.textContent = 'MASTER DELIVERED';
  renderStatusBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-sageMuted';
  renderProgressBar.style.width = '100%';

  logToTerminal(`Master MP4 delivered: ${job.video_url} (${(job.result.file_size_bytes / 1024 / 1024).toFixed(2)} MB in ${job.result.render_time_seconds}s)`);
  if (job.result.audio_status) logToTerminal(job.result.audio_status);

  // Load video player
  videoSource.src = job.video_url;
  masterVideoPlayer.load();
  emptyPlayerState.classList.add('hidden');
  masterVideoPlayer.play().catch(() => {});

  // Update Metadata Bar
  activeVideoTitle.textContent = job.result.title || 'Master Video';
  activeVideoAspect.textContent = job.result.aspect_ratio || '16:9 Cinema';
  activeVideoDuration.textContent = `${job.result.duration}s`;

  // Enable download button
  downloadVideoBtn.href = job.video_url;
  downloadVideoBtn.setAttribute('download', `${job.video_id}.mp4`);
  downloadVideoBtn.classList.remove('pointer-events-none', 'opacity-40');

  resetRenderBtn();
  loadVaultVideos();
}

function resetRenderBtn() {
  startRenderBtn.disabled = false;
  startRenderBtn.innerHTML = `
    <i data-lucide="play" class="w-4 h-4 fill-current"></i>
    <span>Render Video</span>
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
    const videos = data.videos || [];
    vaultCount.textContent = videos.length;

    if (!videos.length) {
      vaultGrid.innerHTML = `
        <div class="col-span-full py-12 text-center text-xs text-zinc-500">
          No rendered videos in vault yet.
        </div>
      `;
      return;
    }

    vaultGrid.innerHTML = '';
    videos.forEach(v => {
      const card = document.createElement('div');
      card.className = 'bg-obsidian border border-borderSub rounded-lg overflow-hidden group cursor-pointer hover:border-zinc-700 transition-all';
      card.innerHTML = `
        <div class="aspect-video bg-zinc-950 relative flex items-center justify-center overflow-hidden">
          ${v.thumb_url ? `<img src="${escapeHtml(v.thumb_url)}" class="w-full h-full object-cover" alt="">` : `<i data-lucide="video" class="w-8 h-8 text-zinc-700"></i>`}
          <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all">
            <span class="w-9 h-9 rounded-full bg-white text-obsidian flex items-center justify-center">
              <i data-lucide="play" class="w-4 h-4 fill-current ml-0.5"></i>
            </span>
          </div>
        </div>
        <div class="p-3 space-y-1">
          <p class="text-xs font-medium text-zinc-200 truncate">${escapeHtml(v.filename)}</p>
          <div class="flex items-center justify-between text-[10px] font-mono text-zinc-500">
            <span>${escapeHtml(v.size_formatted)}</span>
            <span>${escapeHtml(v.created_at)}</span>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        videoSource.src = v.video_url;
        masterVideoPlayer.load();
        emptyPlayerState.classList.add('hidden');
        masterVideoPlayer.play().catch(() => {});

        activeVideoTitle.textContent = v.filename;
        downloadVideoBtn.href = v.video_url;
        downloadVideoBtn.setAttribute('download', v.filename);
        downloadVideoBtn.classList.remove('pointer-events-none', 'opacity-40');

        vaultModal.classList.add('hidden');
      });

      vaultGrid.appendChild(card);
    });

    refreshLucide();
  } catch (err) {
    console.error('Error loading vault:', err);
  }
}
