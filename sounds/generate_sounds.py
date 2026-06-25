#!/usr/bin/env python3
"""
Sound Generator for Ridol FB Tool
Creates WAV files using Python's wave module
Author: Ridol Islam
"""

import os
import sys
import wave
import math
import struct
import random

# Audio parameters
SAMPLE_RATE = 44100  # 44.1kHz
BIT_DEPTH = 16       # 16-bit
MAX_AMPLITUDE = 32767

def generate_sine_wave(duration, frequency, amplitude=0.5):
    """Generate a sine wave sample"""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        value = int(amplitude * MAX_AMPLITUDE * math.sin(2 * math.pi * frequency * t))
        samples.append(value)
    return samples

def generate_square_wave(duration, frequency, amplitude=0.5):
    """Generate a square wave sample"""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        if math.sin(2 * math.pi * frequency * t) > 0:
            value = int(amplitude * MAX_AMPLITUDE)
        else:
            value = -int(amplitude * MAX_AMPLITUDE)
        samples.append(value)
    return samples

def generate_sweep(duration, start_freq, end_freq, amplitude=0.5):
    """Generate a frequency sweep"""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = start_freq + (end_freq - start_freq) * (t / duration)
        value = int(amplitude * MAX_AMPLITUDE * math.sin(2 * math.pi * freq * t))
        samples.append(value)
    return samples

def generate_click():
    """Generate a click sound"""
    samples = []
    # Short high-frequency burst with decay
    for i in range(1000):
        t = i / SAMPLE_RATE
        envelope = math.exp(-t * 100)
        freq = 800 + random.randint(-100, 100)
        value = int(0.7 * MAX_AMPLITUDE * envelope * math.sin(2 * math.pi * freq * t))
        samples.append(value)
    # Add a short silence
    samples.extend([0] * 500)
    return samples

def generate_success():
    """Generate a success sound (rising tone)"""
    samples = []
    # Major chord arpeggio: C-E-G
    notes = [523.25, 659.25, 783.99]  # C4, E4, G4
    for note in notes:
        samples.extend(generate_sine_wave(0.15, note, 0.4))
    # Final high note
    samples.extend(generate_sine_wave(0.3, 1046.50, 0.3))  # C6
    # Add decay
    samples.extend(generate_sine_wave(0.1, 1046.50, 0.1))
    return samples

def generate_fail():
    """Generate a fail sound (descending tone)"""
    samples = []
    # Descending minor chord
    notes = [440.00, 349.23, 293.66]  # A4, F4, D4
    for note in notes:
        samples.extend(generate_sine_wave(0.2, note, 0.4))
    # Low ending
    samples.extend(generate_sine_wave(0.3, 220.00, 0.3))
    samples.extend(generate_sine_wave(0.2, 220.00, 0.1))
    return samples

def generate_done():
    """Generate a completion sound"""
    samples = []
    # Two-tone success
    samples.extend(generate_sine_wave(0.2, 784, 0.5))  # G5
    samples.extend(generate_sine_wave(0.05, 0, 0))     # Silence
    samples.extend(generate_sine_wave(0.3, 1046.50, 0.5))  # C6
    samples.extend(generate_sine_wave(0.5, 1318.51, 0.3))  # E6
    return samples

def generate_startup():
    """Generate a startup sound"""
    samples = []
    # Rising sweep with reverb effect
    samples.extend(generate_sweep(0.5, 200, 800, 0.4))
    samples.extend(generate_sine_wave(0.05, 0, 0))
    samples.extend(generate_sweep(0.3, 800, 1200, 0.3))
    # Short fade
    samples.extend(generate_sine_wave(0.2, 1200, 0.15))
    return samples

def generate_binary_rain():
    """Generate a cyberpunk ambiance with random beeps"""
    samples = []
    duration = 30  # 30 seconds loop
    
    # Background hum
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        # Low background drone
        value1 = int(0.1 * MAX_AMPLITUDE * math.sin(2 * math.pi * 80 * t))
        value2 = int(0.05 * MAX_AMPLITUDE * math.sin(2 * math.pi * 120 * t + 1.5))
        # Random beeps
        beep = 0
        if random.random() < 0.02:  # 2% chance of beep
            freq = random.choice([400, 600, 800, 1000, 1200, 1600])
            beep = int(0.2 * MAX_AMPLITUDE * math.sin(2 * math.pi * freq * t))
        value = value1 + value2 + beep
        samples.append(value)
    
    return samples

def save_wav(filename, samples):
    """Save samples as WAV file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Convert samples to bytes
    data = bytearray()
    for sample in samples:
        # Clamp to 16-bit range
        sample = max(-32768, min(32767, sample))
        data.extend(struct.pack('<h', sample))
    
    # Write WAV file
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)          # Mono
        wav.setsampwidth(2)          # 16-bit
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(data)

def main():
    """Generate all sound effects"""
    print("🎵 Generating sound effects...")
    
    sounds = {
        'click.wav': generate_click,
        'success.wav': generate_success,
        'fail.wav': generate_fail,
        'done.wav': generate_done,
        'startup.wav': generate_startup,
        'binary_rain.wav': generate_binary_rain,
    }
    
    sound_dir = os.path.dirname(os.path.abspath(__file__))
    for filename, generator in sounds.items():
        filepath = os.path.join(sound_dir, filename)
        print(f"  Generating: {filename}")
        samples = generator()
        save_wav(filepath, samples)
        print(f"  ✅ Saved: {filepath}")
    
    print("\n✅ All sound effects generated successfully!")
    print(f"📁 Location: {sound_dir}")

if __name__ == '__main__':
    main()
