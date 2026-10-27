"""Generate a small synthetic Online-Retail-shaped CSV (for CI / quick tests only).
Real runs use data/online_retail_clean.csv produced by your data scripts."""
import csv, random, datetime as dt
random.seed(7)
rows = []
start = dt.datetime(2010, 12, 1, 8, 0)
profiles = [(0.9, 25, 40), (0.4, 8, 20), (0.1, 2, 10), (0.6, 15, 60)]
for cid in range(12000, 12400):
    p = random.choice(profiles)
    for i in range(random.randint(1, max(2, p[1]))):
        day = int(random.random() ** (1 / (p[0] + 0.1)) * 365)
        d = start + dt.timedelta(days=day, minutes=random.randint(0, 600))
        inv = f"{random.randint(536000, 581000)}"
        for _ in range(random.randint(1, 4)):
            rows.append([inv, f"SK{random.randint(100,999)}", "ITEM", random.randint(1, 12),
                         d.strftime("%Y-%m-%d %H:%M:%S"), round(random.uniform(0.5, p[2] / 4), 2), cid, "United Kingdom"])
rows += [["C999999", "SK100", "RETURN", -2, "2011-03-01 10:00:00", 2.5, 12000, "United Kingdom"]]
with open("data/online_retail_clean.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"]); w.writerows(rows)
print(len(rows), "rows")
