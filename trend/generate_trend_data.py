import json
import random
from datetime import datetime, timedelta

# SBCs to track
SBC_LIST = [
    "Raspberry Pi 5",
    "Orange Pi 5", 
    "VIM3",
    "Rock Pi 5",
    "Radxa X4",
    "Banana Pi M5",
    "NVIDIA Jetson Nano",
    "BeagleBone Black"
]

# Generate 8 weeks of realistic trend data
def generate_weekly_data():
    # Start with baseline mentions 8 weeks ago
    baseline = {
        "Raspberry Pi 5": 400,
        "Orange Pi 5": 120,
        "VIM3": 30,
        "Rock Pi 5": 60,
        "Radxa X4": 10,
        "Banana Pi M5": 45,
        "NVIDIA Jetson Nano": 80,
        "BeagleBone Black": 25
    }
    
    # Weekly growth rates (some up, some down, some flat)
    trends = {
        "Raspberry Pi 5": -0.02,  # Slowly declining
        "Orange Pi 5": 0.08,      # Growing steadily
        "VIM3": 0.15,             # Rapid growth (our NPU project!)
        "Rock Pi 5": 0.05,        # Steady growth
        "Radxa X4": 0.25,         # New, fast growth
        "Banana Pi M5": -0.01,    # Slight decline
        "NVIDIA Jetson Nano": 0.03, # Slow growth
        "BeagleBone Black": -0.05   # Decline
    }
    
    data = {}
    current_date = datetime.now()
    
    for week in range(8, -1, -1):  # 9 weeks total (including current)
        week_date = current_date - timedelta(days=7*week)
        week_key = week_date.strftime("%Y-%m-%d")
        data[week_key] = {}
        
        for sbc, base in baseline.items():
            # Calculate mentions based on trend over time
            weeks_from_start = 8 - week
            growth_factor = (1 + trends[sbc]) ** weeks_from_start
            mentions = int(base * growth_factor)
            # Add some random noise (±5%)
            noise = random.randint(-5, 5)
            mentions = max(0, mentions + noise)
            data[week_key][sbc] = mentions
    
    return data

# Generate and save
data = generate_weekly_data()
with open("sbc_trend_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Generated 9 weeks of SBC trend data")
print("\n📊 Latest week data:")
latest = list(data.keys())[-1]
for sbc, mentions in sorted(data[latest].items(), key=lambda x: x[1], reverse=True):
    bar = "█" * (mentions // 10)
    print(f"  {sbc:25} {bar} {mentions}")
