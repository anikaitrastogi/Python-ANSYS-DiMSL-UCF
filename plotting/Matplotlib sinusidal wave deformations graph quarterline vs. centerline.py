import matplotlib.pyplot as plt
#Parse results to read in data without headers
def parse_results_file(filepath):
    s_positions = []
    z_deflections = []

    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip header/label lines (start with a letter)
        if line[0].isalpha():
            continue

        # Try to parse as numeric data
        try:
            parts = line.split()
            if len(parts) == 3:
                # Format: index, s_position, z_deflection
                s_positions.append(float(parts[1]))
                z_deflections.append(float(parts[2]))
            elif len(parts) == 2:
                # Format: s_position, z_deflection (no index column)
                s_positions.append(float(parts[0]))
                z_deflections.append(float(parts[1]))
        except ValueError:
            continue

    return s_positions, z_deflections

# Parse both files
s_center, z_center = parse_results_file("INCLUDE QUARTERLINE RESULTS PATH HERE")
s_quarter, z_quarter = parse_results_file("INCLUDE CENTERLINE RESULTS PATH HERE")

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(s_center, z_center,
        color="steelblue",
        linewidth=2,
        marker="o",
        markersize=4,
        label="Centerline (y = W/2)")

ax.plot(s_quarter, z_quarter,
        color="tomato",
        linewidth=2,
        marker="s",
        markersize=4,
        linestyle="--",
        label="Quarter-line (y = W/4)")

ax.set_xlabel("S Position Along Panel (m)", fontsize=12)
ax.set_ylabel("Z Deflection (m)", fontsize=12)
ax.set_title("ADJUST TITLE HERE", fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
