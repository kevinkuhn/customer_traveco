# Validation Steps for Column Name Fix

## Problem Fixed
Excel export has column names with trailing dots (e.g., `RKdNr.` instead of `RKdNr`), causing the B&T pickup filter to fail silently.

## Solution Implemented
Added `clean_column_names()` method to automatically remove trailing dots from all column names on import.

## Validation Steps

### 1. Open Notebook 02
```bash
jupyter notebook notebooks/02_data_cleaning_and_validation.ipynb
```

### 2. Restart Kernel (CRITICAL!)
- Menu: **Kernel → Restart & Clear Output**
- This ensures the updated `traveco_utils.py` module is reloaded

### 3. Run All Cells
- Menu: **Cell → Run All**
- Or use the "Run All" button

### 4. Expected Results

#### Cell 6 Output (Filtering Rules)
You should see:
```
Filter 2: B&T Abholaufträge (System='B&T' AND empty RKdNr AND empty/placeholder Auftraggeber)
   ✓ Cleaned X column names (removed trailing dots)  ← NEW LINE
   ℹ️  Column 'RKdNr' found (cleaned from 'RKdNr.')  ← Confirmation message
   ℹ️  Excluded B&T pickup orders: ~3,541           ← TARGET NUMBER
```

**Key validation**: The B&T exclusion count should be **~3,541** (matches your manual Excel filter count).

If you still see "0 B&T orders", the module wasn't reloaded - restart kernel again.

#### Cell 32 Output (Quality Report)
```
Retention rate: ~96.3%
Total excluded: ~4,054 orders (513 Lager + 3,541 B&T)
```

### 5. Verify Column Cleaning Worked

Add a test cell after Cell 6:
```python
# Test: Check if column was cleaned
if 'RKdNr' in cleaner.df.columns:
    print("✓ Column cleaning worked: 'RKdNr' (without dot) exists")
elif 'RKdNr.' in cleaner.df.columns:
    print("✗ Column cleaning failed: Still have 'RKdNr.' (with dot)")
else:
    print("⚠️ Neither column found - check data file")
```

### 6. Check for Issues

If you see:
- **"No B&T pickup orders found"**: Module not reloaded → Restart kernel
- **"0 B&T orders excluded"**: Data file issue → Check file path
- **"Column name cleaning would create duplicates"**: Edge case → Contact Claude

### 7. Next Steps After Validation

Once Cell 6 shows **~3,541 B&T orders excluded**:

1. ✅ Run Notebook 03 (feature engineering)
2. ✅ Verify Betriebszentralen mapping (should have ~351 "Unknown" = orders with Auftraggeber "-")
3. ✅ Verify Sparten mapping
4. ✅ Update German meeting summary with corrected counts
5. ✅ Run Notebooks 04-06

## Troubleshooting

### Problem: Still seeing 0 B&T orders
**Solution**:
1. Close notebook
2. Restart Jupyter server completely: `jupyter notebook stop` then `jupyter notebook`
3. Reopen notebook and run all cells

### Problem: Column names still have dots
**Solution**:
1. Check if `clean_column_names()` is being called in `load_order_analysis()`
2. Add debug print: `print(df.columns.tolist())` after loading
3. Verify file path points to correct Excel file

### Problem: Different count than 3,541
**Possible reasons**:
- Different data file (check file date/size)
- Filter logic changed (compare with manual Excel filter)
- Placeholder handling (check for "-" in Auftraggeber column)

---

**Expected timeline**: 5-10 minutes to validate

**Contact**: If validation fails after kernel restart, there may be a deeper issue with the filter logic.
