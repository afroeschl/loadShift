import csv
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CSV_PATH = Path('output/tradingStrategy.csv')

def load_data(csv_path):
    days = OrderedDict()
    with csv_path.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            day_num = int(row['Day'].split()[1])
            days.setdefault(day_num, []).append(row)
    return days

def plot_yearly_overview(days):
    plt.style.use('seaborn-v0_8-whitegrid')
    dates, profits = [], []
    base_date = datetime(2023, 1, 1)

    for day_num, rows in days.items():
        for row in rows:
            if row['Daily Profit'] and 'Profit:' in row['Daily Profit']:
                val = float(row['Daily Profit'].split('Profit:')[1].split('€')[0].strip())
                dates.append(base_date + timedelta(days=day_num - 1))
                profits.append(val)
                break 

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, profits, color='#2980b9', linewidth=2)
    ax.fill_between(dates, profits, color='#2980b9', alpha=0.1)
    
    ax.set_title('Cumulative Yearly Profit', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Profit (€)', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Clean up borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    fig.autofmt_xdate()
    fig.tight_layout()

def plot_day_details(day_number, rows):
    plt.style.use('seaborn-v0_8-whitegrid')
    
    times = [datetime(2023, 1, 1) + timedelta(minutes=15 * i) for i in range(len(rows))]
    prices = [float(r['Price']) for r in rows]
    actions = [int(r['Action']) for r in rows]
    capacity = [float(r['Capacity'].strip('%')) for r in rows]

    buy_times = [t for t, a in zip(times, actions) if a == 1]
    buy_prices = [p for p, a in zip(prices, actions) if a == 1]
    sell_times = [t for t, a in zip(times, actions) if a == 2]
    sell_prices = [p for p, a in zip(prices, actions) if a == 2]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Price Line
    ax1.plot(times, prices, color='#34495e', label='Market Price', linewidth=1.5, alpha=0.8)
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5) # Zero-price reference line

    # Action Markers (with white edges for high contrast)
    ax1.scatter(buy_times, buy_prices, color='#27ae60', marker='^', s=120, edgecolors='white', linewidth=1.5, label='Buy Action', zorder=5)
    ax1.scatter(sell_times, sell_prices, color='#e74c3c', marker='v', s=120, edgecolors='white', linewidth=1.5, label='Sell Action', zorder=5)
    
    ax1.set_ylabel('Electricity Price (€)', color='#34495e', fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#34495e')
    
    # Format X-axis for hours and minutes
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.set_xlabel('Time (HH:MM)', fontsize=11, fontweight='bold')

    # Capacity Line and Area Fill
    ax2 = ax1.twinx()
    ax2.plot(times, capacity, color='#3498db', label='State of Charge', linewidth=2.5)
    ax2.fill_between(times, capacity, color='#3498db', alpha=0.15)
    
    ax2.set_ylabel('State of Charge (%)', color='#2980b9', fontsize=11, fontweight='bold')
    ax2.set_ylim(0, 105)
    ax2.tick_params(axis='y', labelcolor='#2980b9')

    # Styling and Grid
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2.grid(False) 
    
    fig.suptitle(f'Trading Strategy: Day {day_number}', fontsize=16, fontweight='bold', y=0.96)
    
    # Unified Legend at the top
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, 0.90), ncol=4, frameon=True, shadow=True)
    
    fig.tight_layout(rect=[0, 0, 1, 0.88])

def main():
    if not CSV_PATH.exists():
        print(f"Error: '{CSV_PATH}' does not exist.")
        return

    days = load_data(CSV_PATH)
    if not days:
        print("Error: No data found in CSV.")
        return

    plot_yearly_overview(days)
    
    target_day = 1 
    if target_day in days:
        plot_day_details(target_day, days[target_day])

    plt.show()

if __name__ == '__main__':
    main()