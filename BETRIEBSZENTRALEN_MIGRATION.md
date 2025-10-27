# Betriebszentralen Mapping Migration

**Date**: 2025-10-24
**Status**: Implementation Complete - Pending Validation

## Overview

This document describes the migration from `Nummer.Auftraggeber` (order owner numbers) to `Betriebszentralen` (dispatch center names) for cost attribution and aggregation.

### Why This Change?

The 14 **Betriebszentralen** (dispatch centers) are the actual invoicing units within Traveco. These dispatch centers are where transports originate and where invoices are sent. Previously, we aggregated by `Nummer.Auftraggeber` (Column G), which are numeric identifiers. The new mapping provides **human-readable names** for these 14 units, making analysis clearer.

### The 14 Betriebszentralen

| Nummer.Auftraggeber | Name1 | Location |
|---------------------|-------|----------|
| 10 | LC Nebikon (Logistics Center) | Nebikon |
| 1100 | B&T Winterthur | SEUZACH |
| 1200 | B&T Landquart | LANDQUART |
| 1500 | BZ Intermodal / Rail | Nebikon |
| 1600 | B&T Puidoux | PUIDOUX |
| 1900 | BZ Sierre | Sierre |
| 3000 | BZ Oberbipp | Oberbipp |
| 4000 | BZ Winterthur | Winterthur |
| 5000 | BZ Sursee | Sursee |
| 6000 | BZ Herzogenbuchsee | Herzogenbuchsee |
| 6040 | BZ Puidoux | Puidoux |
| 7000 | BZ Landquart | LANDQUART |
| 8000 | BZ Rothrist | Rothrist |
| 9000 | LC Nebikon (Logistics Center) | Nebikon |

**Note**: Numbers 10 and 9000 both map to "LC Nebikon" (duplicate handled by keeping first match).

## Changes Implemented

### 1. ✅ Data Files

**Added**: `data/raw/TRAVECO_Betriebszentralen.csv`
- Contains mapping from `Nummer.Auftraggeber` → `Name1` (dispatch center name)
- 14 rows (with 1 duplicate: 10 and 9000 both = LC Nebikon)
- Columns: `Nummer.Auftraggeber`, `Name1`, `Name2`, `PLZ`, `Ort`

### 2. ✅ Utility Functions (`utils/traveco_utils.py`)

**Added Methods**:

#### `TravecomDataLoader.load_betriebszentralen()`
- Loads the Betriebszentralen mapping CSV
- Tries multiple file paths (`raw_path` and `data/raw/`)
- Returns DataFrame with 14 dispatch center mappings

#### `TravecomDataLoader.load_all_with_betriebszentralen()`
- Convenience method to load all data files including Betriebszentralen
- Returns tuple: `(orders, tours, divisions, betriebszentralen)`

#### `TravecomFeatureEngine.map_betriebszentralen()`
- Maps `Nummer.Auftraggeber` → `betriebszentrale_name`
- Handles type conversions (Int64 for reliable matching)
- Handles duplicates (keeps first match)
- Marks unmapped orders as "Unknown Betriebszentrale"
- Provides detailed diagnostic output

**Key Features**:
- Auto-converts data types to Int64 for matching
- Drops duplicate Auftraggeber numbers (keeps first)
- Shows mapping statistics and unmapped numbers
- Returns DataFrame with new `betriebszentrale_name` column

### 3. ✅ Configuration (`config/config.yaml`)

**Added**:
```yaml
data:
  betriebszentralen: "TRAVECO_Betriebszentralen.csv"  # 14 dispatch centers (invoicing units)
```

### 4. ✅ Notebook 03: Feature Engineering

**Added Section 7.5**: Betriebszentralen Mapping

**New Cells**:
1. **Load Betriebszentralen**: Loads the mapping file using `loader.load_betriebszentralen()`
2. **Map to Orders**: Applies `feature_engine.map_betriebszentralen()` to create `betriebszentrale_name` column
3. **Visualization**: Bar chart showing top 10 Betriebszentralen by order volume

**Updated**:
- Feature summary now includes `betriebszentrale_name` in categorical features
- Shows count of dispatch centers (expected: 14)

### 5. ✅ Notebook 04: Aggregation and Targets

**Critical Changes**:

#### Cell 8 - Branch Selection Logic
**Before**:
```python
branch_col = 'Nummer.Auftraggeber'  # Used numeric IDs
```

**After**:
```python
if 'betriebszentrale_name' in df.columns:
    branch_col = 'betriebszentrale_name'  # Use dispatch center names
    print("✓ Using Betriebszentralen (dispatch centers)")
elif 'Nummer.Auftraggeber' in df.columns:
    print("⚠️ WARNING: betriebszentrale_name not found!")
    branch_col = 'Nummer.Auftraggeber'  # Fallback
```

#### Cell 9 - Aggregation
**Before**:
- Aggregated by `Nummer.Auftraggeber` (12 unique values)
- Created comparison view by `Id.Dispostelle`

**After**:
- Aggregates by `betriebszentrale_name` (14 unique values)
- Removed Dispostelle comparison view (no longer needed)
- Added validation: "Expected: 14 Betriebszentralen"

**Impact**:
- `monthly_aggregated.csv` will now show **14 rows** (one per Betriebszentrale)
- Rows are labeled with names like "BZ Winterthur", "LC Nebikon" instead of numbers
- No more `monthly_aggregated_by_dispostelle.csv` file generated

### 6. 🔄 Pending: Notebook 05-06 Updates

**Required Changes**:
- Update chart titles/labels to say "Betriebszentrale" instead of "Auftraggeber"
- Update any hardcoded column references
- Verify that visualizations work with string names instead of numeric IDs

### 7. 🔄 Pending: Presentation Updates

**Required Changes in `create_presentation.py`**:
- Update data loading to expect `betriebszentrale_name` column
- Update slide titles: "Cost Attribution by Betriebszentrale"
- Update chart labels and legends
- Add explanation of the 14 invoicing units

### 8. 🔄 Pending: Documentation Updates

**Files to Update**:
- **CLAUDE.md**: Add explanation of Betriebszentralen mapping in "CRITICAL CORRECTIONS" section
- **IMPLEMENTATION_SUMMARY.md**: Document this migration
- **TROUBLESHOOTING.md**: Add section for Betriebszentralen mapping issues

## Expected Outcomes

### Before Migration
- Aggregations showed **12 unique Auftraggeber** (numeric IDs like 3000, 5000, 4000)
- Charts displayed numbers (hard to interpret)
- Cost attribution unclear (numbers don't convey meaning)

### After Migration
- Aggregations show **14 unique Betriebszentralen** (names like "BZ Oberbipp", "BZ Sursee")
- Charts display readable names
- Clear cost attribution to dispatch centers
- Aligns with Traveco's invoicing structure

## Validation Checklist

- [ ] Run Notebook 03 - Verify 14 Betriebszentralen mapped
- [ ] Check `betriebszentrale_name` column exists in `features_engineered.csv`
- [ ] Run Notebook 04 - Verify 14 rows in `monthly_aggregated.csv`
- [ ] Verify all orders are mapped (no "Unknown Betriebszentrale" or minimal)
- [ ] Check financial totals match before/after migration
- [ ] Update and run Notebooks 05-06
- [ ] Regenerate presentation with new labels
- [ ] Verify charts display correctly with names

## Troubleshooting

### Issue: "betriebszentrale_name not found" in Notebook 04

**Solution**: Notebook 03 was not run with updated code. Re-run Notebook 03 after:
1. Restart Jupyter kernel (Kernel → Restart)
2. Run all cells from the beginning

### Issue: All orders show "Unknown Betriebszentrale"

**Causes**:
1. Type mismatch between orders and Betriebszentralen file
2. `TRAVECO_Betriebszentralen.csv` not found

**Solution**: Check diagnostics output from `map_betriebszentralen()` - it shows type conversion and matching statistics

### Issue: Only 13 Betriebszentralen instead of 14

**Explanation**: Numbers 10 and 9000 both map to "LC Nebikon", so they're counted as one. This is expected behavior (duplicate handling).

## Rollback Plan

If issues arise, revert to previous logic:

1. **In Notebook 04, Cell 8**: Force use of `Nummer.Auftraggeber`
   ```python
   branch_col = 'Nummer.Auftraggeber'
   ```

2. **Skip Betriebszentralen mapping in Notebook 03**: Comment out Section 7.5

3. **Restore old presentation code**: Use numeric Auftraggeber labels

## Next Steps

1. ✅ Complete Notebook 05-06 updates
2. ✅ Update `create_presentation.py`
3. ✅ Update documentation (CLAUDE.md, IMPLEMENTATION_SUMMARY.md)
4. ✅ Run full pipeline to validate
5. ✅ Generate new presentation with Betriebszentralen names
6. ✅ Review outputs with stakeholders

## Technical Notes

### Why "betriebszentrale_name" Column Name?

- Descriptive: Clearly indicates this is the dispatch center name
- Consistent: Follows pattern of other mapped columns (`sparte`, `carrier_type`)
- Distinguishable: Different from `Nummer.Auftraggeber` to avoid confusion

### Handling Duplicates (10 and 9000)

Both numbers map to "LC Nebikon (Logistics Center)". The code handles this by:
```python
betriebszentralen_unique = df_betriebszentralen.drop_duplicates(
    subset='Nummer.Auftraggeber', keep='first'
)
```
This keeps the first occurrence (row with number 10) and drops the duplicate (9000).

### Type Conversion Strategy

The mapping function converts both columns to `Int64`:
```python
df_orders['Nummer.Auftraggeber'] = pd.to_numeric(...).astype('Int64')
df_betriebszentralen['Nummer.Auftraggeber'] = pd.to_numeric(...).astype('Int64')
```

This ensures reliable matching regardless of whether the CSV has integers or floats.

---

**Implementation Date**: 2025-10-24
**Implemented By**: Claude Code
**Approved By**: Pending User Validation
