import glob, os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs(r"..\cases\plots", exist_ok=True)

cases = {
    "Baseline_Example1": glob.glob(r"..\cases\baseline_example1\**\Sequential_simulation.csv", recursive=True),
    "Baseline_Example8": glob.glob(r"..\cases\baseline_example8\**\Sequential_simulation.csv", recursive=True),
    "Controlled_Arch_Scaling": glob.glob(r"..\cases\exp_arch_scaling\**\Sequential_simulation.csv", recursive=True),
}

dfs = []
for name, files in cases.items():
    if files:
        df = pd.read_csv(files[0])
        df.columns = [c.strip() for c in df.columns]
        df["Experiment"] = name
        dfs.append(df)
        print(f"Loaded {name}: {len(df)} rows")

if not dfs:
    print("No Sequential_simulation.csv files found in ..\\cases\\")
    exit(1)

all_df = pd.concat(dfs, ignore_index=True)

arch_col = next((c for c in all_df.columns if "architecture" in c.lower()), all_df.columns[0])
dev_col = next((c for c in all_df.columns if "edge devices" in c.lower() or "devices" in c.lower()), None)
delay_col = next((c for c in all_df.columns if "average waiting" in c.lower() or "execution delay" in c.lower() or "delay" in c.lower()), None)
succ_col = next((c for c in all_df.columns if "tasks successfully" in c.lower() or "success" in c.lower()), None)
energy_col = next((c for c in all_df.columns if "energy consumption" in c.lower() or "energy" in c.lower()), None)

metrics = [c for c in [delay_col, succ_col, energy_col] if c]
summary = all_df.groupby(["Experiment", arch_col])[metrics].mean(numeric_only=True).round(3)
print("\n=== SUMMARY TABLE (MEAN ACROSS SCENARIOS) ===")
print(summary.to_string())
summary.to_csv(r"..\cases\plots\summary_table.csv")

fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 4))
if len(metrics) == 1:
    axes = [axes]
for ax, col in zip(axes, metrics):
    pivot = all_df.pivot_table(index=arch_col, columns="Experiment", values=col, aggfunc="mean")
    pivot.plot(kind="bar", ax=ax, rot=20)
    ax.set_title(col[:35], fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(r"..\cases\plots\architecture_comparison.png", dpi=150)

exp_df = all_df[all_df["Experiment"] == "Controlled_Arch_Scaling"]
if not exp_df.empty and dev_col and metrics:
    fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 4))
    if len(metrics) == 1:
        axes = [axes]
    for ax, col in zip(axes, metrics):
        for arch, grp in exp_df.groupby(arch_col):
            grp_sorted = grp.sort_values(dev_col)
            ax.plot(grp_sorted[dev_col], grp_sorted[col], marker="o", label=arch)
        ax.set_xlabel("Edge Devices")
        ax.set_title(col[:35], fontsize=10)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(r"..\cases\plots\controlled_scaling_curves.png", dpi=150)

print("\nSaved plots and summary_table.csv to ..\\cases\\plots\\")
