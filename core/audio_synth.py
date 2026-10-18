import math
import wave
import struct
import numpy as np

SAMPLE_RATE = 44100

def note_freq(name: str) -> float:
    """Map common musical note names to frequency in Hz."""
    notes = {
        'C2': 65.41, 'D2': 73.42, 'E2': 82.41, 'F#2': 92.50, 'G#2': 103.83, 'A2': 110.00, 'B2': 123.47,
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F#3': 185.00, 'G#3': 207.65, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F#4': 369.99, 'G#4': 415.30, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F#5': 739.99, 'G#5': 830.61, 'A5': 880.00, 'B5': 987.77,
        'C6': 1046.50, 'E6': 1318.51
    }
    return notes.get(name, 440.0)

def generate_pad_voice(freq: float, duration: float, t_start: float, total_samples: int, volume: float = 0.35) -> tuple[np.ndarray, np.ndarray]:
    """Generates a warm, lush stereo ambient pad with stereo detuning."""
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    start_idx = int(t_start * SAMPLE_RATE)
    dur_samples = int(duration * SAMPLE_RATE)
    end_idx = min(start_idx + dur_samples, total_samples)
    actual_len = end_idx - start_idx
    if actual_len <= 0:
        return left, right

    t = np.linspace(0, duration, dur_samples, endpoint=False)[:actual_len]

    # Smooth attack and long decay envelope
    attack_len = int(SAMPLE_RATE * min(1.2, duration * 0.3))
    release_len = int(SAMPLE_RATE * min(1.5, duration * 0.4))
    env = np.ones(actual_len, dtype=np.float32)

    if attack_len > 0 and attack_len < actual_len:
        env[:attack_len] = np.sin(np.linspace(0, np.pi / 2, attack_len)) ** 2
    if release_len > 0 and release_len < actual_len:
        env[-release_len:] = np.cos(np.linspace(0, np.pi / 2, release_len)) ** 2

    # Left channel: fundamental + soft harmonic + detune
    sig_l = (
        0.55 * np.sin(2 * np.pi * freq * t) +
        0.25 * np.sin(2 * np.pi * (freq * 1.002) * t) +
        0.12 * np.sin(2 * np.pi * (freq * 2.0) * t) +
        0.08 * np.sin(2 * np.pi * (freq * 0.5) * t)
    ) * env * volume

    # Right channel: slight pitch offset for deep stereo space
    sig_r = (
        0.55 * np.sin(2 * np.pi * (freq * 0.998) * t) +
        0.25 * np.sin(2 * np.pi * (freq * 1.003) * t) +
        0.12 * np.sin(2 * np.pi * (freq * 2.001) * t) +
        0.08 * np.sin(2 * np.pi * (freq * 0.5) * t)
    ) * env * volume

    left[start_idx:end_idx] += sig_l
    right[start_idx:end_idx] += sig_r
    return left, right

def generate_chime(freq: float, t_start: float, total_samples: int, volume: float = 0.28) -> tuple[np.ndarray, np.ndarray]:
    """Generates a crystalline bell chime for scene titles or logo reveals."""
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    start_idx = int(t_start * SAMPLE_RATE)
    dur_samples = int(4.0 * SAMPLE_RATE) # 4s decay
    end_idx = min(start_idx + dur_samples, total_samples)
    actual_len = end_idx - start_idx
    if actual_len <= 0:
        return left, right

    t = np.linspace(0, 4.0, dur_samples, endpoint=False)[:actual_len]
    env = np.exp(-t * 2.2) # Fast acoustic decay

    sig_l = (
        0.60 * np.sin(2 * np.pi * freq * t) +
        0.28 * np.sin(2 * np.pi * freq * 2.756 * t) +
        0.12 * np.sin(2 * np.pi * freq * 5.404 * t)
    ) * env * volume

    sig_r = (
        0.60 * np.sin(2 * np.pi * (freq * 1.0015) * t) +
        0.28 * np.sin(2 * np.pi * freq * 2.760 * t) +
        0.12 * np.sin(2 * np.pi * freq * 5.400 * t)
    ) * env * volume

    left[start_idx:end_idx] += sig_l
    right[start_idx:end_idx] += sig_r
    return left, right

def generate_riser(t_start: float, duration: float, total_samples: int, volume: float = 0.20) -> tuple[np.ndarray, np.ndarray]:
    """Generates a smooth white-noise riser sweep leading up to a scene transition."""
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    start_idx = int(t_start * SAMPLE_RATE)
    dur_samples = int(duration * SAMPLE_RATE)
    end_idx = min(start_idx + dur_samples, total_samples)
    actual_len = end_idx - start_idx
    if actual_len <= 0:
        return left, right

    t = np.linspace(0, 1, actual_len, endpoint=False)
    # Exponential frequency sweep
    freq_sweep = 120 + 700 * (t ** 2.5)
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE
    env = t ** 2.2 * volume

    noise = (np.random.rand(actual_len) * 2 - 1) * 0.25 * env
    tone = np.sin(phase) * env

    left[start_idx:end_idx] += (tone * 0.7 + noise * 0.3)
    right[start_idx:end_idx] += (tone * 0.7 + noise * 0.3)
    return left, right

def synthesize_soundtrack(duration: float, mood: str = "cinematic_tech", output_wav: str = "soundtrack.wav") -> str:
    """Synthesizes a full multi-track stereo master soundtrack based on mood and timing."""
    total_samples = int(duration * SAMPLE_RATE)
    master_l = np.zeros(total_samples, dtype=np.float32)
    master_r = np.zeros(total_samples, dtype=np.float32)

    # Progression based on mood
    if mood == "minimalist_apple":
        # Warm, restrained chords: E Maj -> C# min -> A Maj9 -> E Maj
        chords = [
            (0.0, min(duration, 7.0), ['E2', 'B2', 'E3', 'G#3', 'B3']),
            (6.5, min(duration - 6.5, 7.0), ['C#2', 'G#2', 'C#3', 'E3', 'B3']),
            (13.0, min(duration - 13.0, 8.0), ['A2', 'E3', 'A3', 'C#4', 'E4']),
            (20.0, min(duration - 20.0, 10.0), ['E2', 'B2', 'E3', 'G#3', 'B3', 'E4'])
        ]
        chimes = [0.2, 5.0, 13.0, max(0.0, duration - 6.0)]
    elif mood == "high_energy_saas":
        # Modern tech beat: D min -> F Maj -> C Maj -> G min
        chords = [
            (0.0, min(duration, 4.0), ['D2', 'A2', 'D3', 'F3', 'A3']),
            (3.8, min(duration - 3.8, 4.0), ['F2', 'C3', 'F3', 'A3', 'C4']),
            (7.5, min(duration - 7.5, 4.0), ['C2', 'G2', 'C3', 'E3', 'G3']),
            (11.2, min(duration - 11.2, 8.0), ['G2', 'D3', 'G3', 'Bb3', 'D4'])
        ]
        chimes = [0.1, 3.8, 7.5, 11.2]
    else: # cinematic_tech default
        chords = [
            (0.0, min(duration, 5.0), ['E2', 'B2', 'E3', 'G#3', 'B3']),
            (4.8, min(duration - 4.8, 5.0), ['C#2', 'G#2', 'C#3', 'E3', 'B3']),
            (9.5, min(duration - 9.5, 6.0), ['A2', 'E3', 'A3', 'C#4', 'E4']),
            (15.0, min(duration - 15.0, 15.0), ['B2', 'F#3', 'B3', 'D#4', 'F#4'])
        ]
        chimes = [0.1, 4.8, 9.5, max(0.0, duration - 5.0)]

    # Add chords
    for t_start, dur, notes in chords:
        if t_start >= duration:
            break
        for n in notes:
            vl, vr = generate_pad_voice(note_freq(n), dur, t_start, total_samples, volume=0.18 / len(notes))
            master_l += vl
            master_r += vr

    # Add chime accents
    for c_time in chimes:
        if c_time < duration:
            cl, cr = generate_chime(note_freq('E5'), c_time, total_samples, volume=0.22)
            master_l += cl
            master_r += cr

    # Add subtle riser before finale (approx 3.5s before end)
    riser_start = max(1.0, duration - 4.5)
    rl, rr = generate_riser(riser_start, 2.5, total_samples, volume=0.15)
    master_l += rl
    master_r += rr

    # Master limiter & soft normalization
    peak = max(np.max(np.abs(master_l)), np.max(np.abs(master_r)), 1e-6)
    target_peak = 0.88
    if peak > target_peak:
        norm_factor = target_peak / peak
    else:
        norm_factor = target_peak / max(peak, 0.4)

    master_l = np.clip(master_l * norm_factor, -0.98, 0.98)
    master_r = np.clip(master_r * norm_factor, -0.98, 0.98)

    # Convert to 16-bit PCM
    pcm_l = (master_l * 32767).astype(np.int16)
    pcm_r = (master_r * 32767).astype(np.int16)
    interleaved = np.empty((total_samples * 2,), dtype=np.int16)
    interleaved[0::2] = pcm_l
    interleaved[1::2] = pcm_r

    # Write WAV file
    with wave.open(output_wav, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(interleaved.tobytes())

    return output_wav
