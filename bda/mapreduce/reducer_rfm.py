#!/usr/bin/env python3
"""Hadoop Streaming reducer: per customer -> Recency, Frequency, Monetary.
REF_DATE env var (YYYY-MM-DD) = snapshot date; default 2011-12-10."""
import sys, os, datetime as dt
ref = dt.date.fromisoformat(os.environ.get("REF_DATE", "2011-12-10"))

def emit(cust, invoices, last, total):
    print(f"{cust}\t{(ref - last).days}\t{len(invoices)}\t{total:.2f}")

cur, invoices, last, total = None, set(), None, 0.0
for line in sys.stdin:
    cust, val = line.rstrip("\n").split("\t", 1)
    inv, d, amt = val.split(",")
    d = dt.date.fromisoformat(d)
    if cust != cur:
        if cur is not None:
            emit(cur, invoices, last, total)
        cur, invoices, last, total = cust, set(), d, 0.0
    invoices.add(inv); total += float(amt)
    if d > last: last = d
if cur is not None:
    emit(cur, invoices, last, total)
