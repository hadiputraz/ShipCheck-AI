from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / "data"
INBOX_DIR = DATA_DIR / "inbox"

print("ShipCheck AI - Dataset Inspector")
print("=" * 40)

print(f"Data directory: {DATA_DIR}")
print(f"Inbox directory: {INBOX_DIR}")

if not INBOX_DIR.exists():
    print("\nERROR: inbox directory not found.")
    print("Check the extracted dataset structure.")
    exit()

files = list(INBOX_DIR.iterdir())

print(f"\nFiles found: {len(files)}")

for file in files[:5]:
    print(f" - {file.name}")