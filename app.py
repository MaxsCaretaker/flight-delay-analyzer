import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── Theme ───────────────────────────────────────────
BG = "#1e1e2e"
CARD = "#2a2a3e"
ACCENT = "#4fa3e0"
TEXT = "#ffffff"
SUBTEXT = "#aaaacc"
GREEN = "#4caf50"
BLUE = "#42a5f5"

# ── Load Data ────────────────────────────────────────
print("Loading data...")
df = pd.read_csv("flights_clean.csv", low_memory=False)
df["dep_delay"] = pd.to_numeric(df["dep_delay"], errors="coerce")
df["arr_delay"] = pd.to_numeric(df["arr_delay"], errors="coerce")
df["cancelled"] = pd.to_numeric(df["cancelled"], errors="coerce")

AIRLINE_NAMES = {
    "AA": "American", "DL": "Delta", "UA": "United",
    "WN": "Southwest", "AS": "Alaska", "B6": "JetBlue",
    "F9": "Frontier", "G4": "Allegiant", "HA": "Hawaiian", "NK": "Spirit"
}

airlines = sorted(df["airline"].dropna().unique())
airports = sorted(df["origin"].dropna().unique())

# ── Root ─────────────────────────────────────────────
root = tk.Tk()
root.title("✈️ Flight Delay Analyzer")
root.geometry("900x700")
root.configure(bg=BG)
root.resizable(False, False)

# ── Header ───────────────────────────────────────────
header = tk.Frame(root, bg=ACCENT, pady=15)
header.pack(fill="x")
tk.Label(header, text="✈️  Flight Delay Analyzer",
         font=("Segoe UI", 22, "bold"), bg=ACCENT, fg=TEXT).pack()
tk.Label(header, text="Explore U.S. flight delay data — Jan 2024",
         font=("Segoe UI", 10), bg=ACCENT, fg="#ddd").pack()

# ── Filter Card ──────────────────────────────────────
filter_card = tk.Frame(root, bg=CARD, padx=20, pady=15)
filter_card.pack(fill="x", padx=20, pady=15)

tk.Label(filter_card, text="Filters", font=("Segoe UI", 13, "bold"),
         bg=CARD, fg=ACCENT).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

# Airline filter
tk.Label(filter_card, text="Airline", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 5))
airline_var = tk.StringVar(value="All")
airline_combo = ttk.Combobox(filter_card, textvariable=airline_var, width=15,
                              values=["All"] + [f"{k} — {v}" for k, v in AIRLINE_NAMES.items() if k in airlines])
airline_combo.grid(row=2, column=0, padx=(0, 15))

# Origin filter
tk.Label(filter_card, text="Origin Airport", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w", padx=(0, 5))
origin_var = tk.StringVar(value="All")
origin_combo = ttk.Combobox(filter_card, textvariable=origin_var, width=10,
                             values=["All"] + airports)
origin_combo.grid(row=2, column=1, padx=(0, 15))

# Chart type
tk.Label(filter_card, text="Chart", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=(0, 5))
chart_var = tk.StringVar(value="Avg Delay by Airline")
chart_combo = ttk.Combobox(filter_card, textvariable=chart_var, width=22, values=[
    "Avg Delay by Airline",
    "Avg Delay by Airport",
    "Delay Causes Breakdown",
    "Cancellation Rate by Airline"
])
chart_combo.grid(row=2, column=2, padx=(0, 15))

# Analyze button
def make_btn(parent, text, cmd, color):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg=TEXT, font=("Segoe UI", 10, "bold"),
                     relief="flat", padx=12, pady=6, cursor="hand2")

analyze_btn_placeholder = tk.Frame(filter_card)
analyze_btn_placeholder.grid(row=2, column=3, padx=5)

# ── Chart Area ───────────────────────────────────────
chart_frame = tk.Frame(root, bg=BG)
chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

canvas_holder = [None]

def show_chart(fig):
    if canvas_holder[0]:
        canvas_holder[0].get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas_holder[0] = canvas

# ── Analysis Logic ───────────────────────────────────
def run_analysis():
    plt.close("all")
    filtered = df.copy()

    # Apply airline filter
    airline_sel = airline_var.get()
    if airline_sel != "All":
        code = airline_sel.split(" — ")[0]
        filtered = filtered[filtered["airline"] == code]

    # Apply origin filter
    origin_sel = origin_var.get()
    if origin_sel != "All":
        filtered = filtered[filtered["origin"] == origin_sel]

    if filtered.empty:
        messagebox.showwarning("No Data", "No flights match your filters.")
        return

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#2a2a3e")

    chart = chart_var.get()

    if chart == "Avg Delay by Airline":
        data = filtered.groupby("airline")["arr_delay"].mean().sort_values(ascending=False)
        data.index = [AIRLINE_NAMES.get(x, x) for x in data.index]
        bars = ax.bar(data.index, data.values, color=ACCENT)
        ax.set_title("Average Arrival Delay by Airline (minutes)", color=TEXT, fontsize=13)
        ax.set_ylabel("Avg Delay (min)", color=SUBTEXT)
        ax.tick_params(colors=TEXT)
        ax.axhline(0, color="white", linewidth=0.5, linestyle="--")
        for bar, val in zip(bars, data.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.1f}", ha="center", color=TEXT, fontsize=9)

    elif chart == "Avg Delay by Airport":
        data = filtered.groupby("origin")["arr_delay"].mean().sort_values(ascending=False).head(15)
        bars = ax.bar(data.index, data.values, color="#7c6af7")
        ax.set_title("Top 15 Airports by Avg Arrival Delay (minutes)", color=TEXT, fontsize=13)
        ax.set_ylabel("Avg Delay (min)", color=SUBTEXT)
        ax.tick_params(colors=TEXT)
        ax.axhline(0, color="white", linewidth=0.5, linestyle="--")

    elif chart == "Delay Causes Breakdown":
        causes = {
            "Carrier": filtered["carrier_delay"].mean(),
            "Weather": filtered["weather_delay"].mean(),
            "NAS": filtered["nas_delay"].mean(),
        }
        causes = {k: v for k, v in causes.items() if pd.notna(v)}
        colors = [ACCENT, "#ff7043", GREEN]
        ax.pie(causes.values(), labels=causes.keys(), colors=colors,
               autopct="%1.1f%%", textprops={"color": TEXT})
        ax.set_title("Delay Causes Breakdown", color=TEXT, fontsize=13)

    elif chart == "Cancellation Rate by Airline":
        data = filtered.groupby("airline")["cancelled"].mean() * 100
        data = data.sort_values(ascending=False)
        data.index = [AIRLINE_NAMES.get(x, x) for x in data.index]
        bars = ax.bar(data.index, data.values, color=["#ef5350"] * len(data))
        ax.set_title("Cancellation Rate by Airline (%)", color=TEXT, fontsize=13)
        ax.set_ylabel("Cancellation Rate (%)", color=SUBTEXT)
        ax.tick_params(colors=TEXT)
        for bar, val in zip(bars, data.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{val:.1f}%", ha="center", color=TEXT, fontsize=9)

    plt.tight_layout()
    show_chart(fig)

# ── Stats Bar ────────────────────────────────────────
stats_frame = tk.Frame(root, bg=CARD, pady=8)
stats_frame.pack(fill="x", padx=20, pady=(0, 10))

total = len(df)
avg_delay = df["arr_delay"].mean()
cancel_rate = df["cancelled"].mean() * 100

for text in [
    f"✈️  Total Flights: {total:,}",
    f"⏱  Avg Arrival Delay: {avg_delay:.1f} min",
    f"❌  Cancellation Rate: {cancel_rate:.1f}%"
]:
    tk.Label(stats_frame, text=text, font=("Segoe UI", 10),
             bg=CARD, fg=TEXT).pack(side="left", padx=20)

# Create analyze button now that run_analysis is defined
make_btn(filter_card, "Analyze", run_analysis, BLUE).grid(row=2, column=3, padx=5)

# Run once on load
run_analysis()
def on_close():
    plt.close("all")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()