#!/usr/bin/env python3
"""Hadoop Streaming mapper. Input: cleaned Online Retail CSV.
Emits: CustomerID <TAB> InvoiceNo,InvoiceDate,LineAmount"""
import sys, csv
for r in csv.reader(sys.stdin):
    if not r or r[0] == "InvoiceNo" or len(r) < 8:
        continue
    inv, qty, date, price, cust = r[0], r[3], r[4], r[5], r[6]
    try:
        q, p = int(float(qty)), float(price)
        cust = str(int(float(cust)))
    except ValueError:
        continue
    if inv.startswith("C") or q <= 0 or p <= 0:
        continue
    print(f"{cust}\t{inv},{date[:10]},{q*p:.2f}")
