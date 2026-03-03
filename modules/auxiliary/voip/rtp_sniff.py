# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import os
import subprocess
import shutil

from rootmap import ROOT 

REQUIRED_OPTIONS = {"INTERFACE": "example: eth0"}


def execute(options):
    interface = options.get("INTERFACE")
    # --- DYNAMIC PATH LOGIC ---
    # Internal path for Storm's innards
    src_dir = os.path.join(ROOT, "external", "source", "binary")
    binary = os.path.join(src_dir, "rtp_sniff")
    # Output path for User (Current Working Directory)
    output_pcm = os.path.join(os.getcwd(), "storm_capture.pcm")
    output_wav = os.path.join(os.getcwd(), "storm_capture.wav")

    print(f"[*] Sniffing on {interface}")
    print(f"[*] Output will be saved at: {os.getcwd()}")
    print("[*] Press Ctrl+C to stop.")

    try:
        # Run binary with arguments: interface and output_path
        subprocess.run(["sudo", binary, interface, output_pcm])
    except KeyboardInterrupt:
        print("\n[*] Sniffing stopped by user.")

    # Automatic Conversion to WAV
    if os.path.exists(output_pcm):
        if shutil.which("ffmpeg"):
            print("[*] Converting raw PCM to WAV...")
            # G.711 mu-law (standar VoIP)
            conv_cmd = f"ffmpeg -y -f u8 -ar 8000 -ac 1 -i {output_pcm} {output_wav} > /dev/null 2>&1"
            os.system(conv_cmd)

            if os.path.exists(output_wav):
                os.remove(output_pcm)
                print(f"[+] Success! Final Audio: {output_wav}")
            else:
                print("[!] Conversion failed. Raw file kept at storm_capture.pcm")
        else:
            print(f"[!] ffmpeg not found. Raw audio saved as: {output_pcm}")
