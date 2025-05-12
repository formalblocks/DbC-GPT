import subprocess
import time

ASSISTANTS = [
    "4o-mini",
    "erc-1155-001-3-16",
    "erc-1155-005-3-16",
    "erc-1155-010-3-16",
    "erc-1155-001-5-16",
    "erc-1155-005-5-16",
    "erc-1155-010-5-16",
    "erc-1155-001-7-16",
    "erc-1155-005-7-16"
]

for assistant in ASSISTANTS:
    print(f"Running for assistant: {assistant}")
    cmd = [
        "python3", "-m", "verifier.main",
        "--requested", "erc1155",
        "--context", "",
        "--runs", "10",
        "--assistant", assistant
    ]
    subprocess.run(cmd)
    time.sleep(5)