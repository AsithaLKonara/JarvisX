#!/usr/bin/env python3
"""
Monitor Hugging Face Space build status
"""

import requests
import time
import sys

SPACE_URL = "https://AsithaLKonara-jarvis-llm-brain.hf.space"
CHECK_INTERVAL = 300  # seconds (5 minutes)

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                                                                  ║")
print("║        ⏳ Waiting for Space to be ready...                       ║")
print("║                                                                  ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()
print(f"🌐 Space URL: {SPACE_URL}")
print(f"🔄 Checking every 5 minutes...")
print("💡 Press Ctrl+C to stop monitoring")
print()

start_time = time.time()
attempt = 0

try:
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)
        elapsed_min = elapsed // 60
        elapsed_sec = elapsed % 60
        
        try:
            response = requests.get(SPACE_URL, timeout=10)
            
            if response.status_code == 200:
                print()
                print("╔══════════════════════════════════════════════════════════════════╗")
                print("║                                                                  ║")
                print("║        ✅ SPACE IS RUNNING!                                      ║")
                print("║                                                                  ║")
                print("╚══════════════════════════════════════════════════════════════════╝")
                print()
                print(f"⏱️  Total wait time: {elapsed_min}m {elapsed_sec}s")
                print()
                print("🎯 Next: Configure Jarvis")
                print("─" * 68)
                print()
                print("export CLOUD_LLM_URL=\"https://AsithaLKonara-jarvis-llm-brain.hf.space\"")
                print("export DISABLE_HELAGPT=true")
                print("python3 main.py")
                print()
                sys.exit(0)
            elif response.status_code == 503:
                print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] Attempt {attempt}: Still building... ⚙️")
            else:
                print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] Attempt {attempt}: HTTP {response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] Attempt {attempt}: Timeout (Space still starting)")
        except requests.exceptions.RequestException as e:
            print(f"[{elapsed_min:02d}:{elapsed_sec:02d}] Attempt {attempt}: Error - {e}")
        
        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print()
    print("⏹️  Monitoring stopped")
    print(f"⏱️  Waited: {elapsed_min}m {elapsed_sec}s")
    print()
    print("💡 Check status manually:")
    print(f"   {SPACE_URL}")

