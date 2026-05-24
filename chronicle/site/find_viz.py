with open("styles.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Search for 'viz-stack':")
for idx, line in enumerate(lines):
    if "viz-stack" in line or "stack-3d" in line:
        print(f"Line {idx+1}: {line.strip()}")
