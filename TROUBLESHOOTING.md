# Traveco Analysis - Troubleshooting Guide

## Error: `AttributeError: 'TravecomFeatureEngine' object has no attribute 'map_customer_divisions'`

### Problem
This error occurs when running notebook 03 after the `traveco_utils.py` file has been updated. Python caches the old version of the module in memory.

### Solution Options

#### Option 1: Restart Kernel (Recommended)
The easiest and safest solution:

1. In Jupyter: **Kernel → Restart & Run All**
2. This will reload all modules with the latest code
3. All cells will re-execute from the beginning

#### Option 2: Reload Module Manually
If you don't want to restart the entire kernel:

Add this cell and run it BEFORE the cell that uses `map_customer_divisions`:

```python
# Force reload of traveco_utils module
import importlib
import sys
if 'utils.traveco_utils' in sys.modules:
    importlib.reload(sys.modules['utils.traveco_utils'])

# Re-import the classes
from utils.traveco_utils import (
    ConfigLoader,
    TravecomDataLoader,
    TravecomFeatureEngine,
    load_processed_data,
    save_processed_data
)

# Re-create the feature_engine instance
feature_engine = TravecomFeatureEngine(config)

print("✓ Module reloaded successfully")
```

#### Option 3: Modify Imports (Already Added)
The notebook has been updated with a comment showing how to reload. Uncomment these lines in cell 2:

```python
# IMPORTANT: If you've updated traveco_utils.py, restart the kernel or uncomment:
import importlib
if 'utils.traveco_utils' in sys.modules:
    importlib.reload(sys.modules['utils.traveco_utils'])
```

---

## Verification

After applying any solution, verify the method exists by running:

```python
# Check if method is available
if hasattr(feature_engine, 'map_customer_divisions'):
    print("✓ map_customer_divisions method is available")
else:
    print("✗ Method not found - try restarting kernel")
```

---

## Other Common Issues

### Issue: "FileNotFoundError: Configuration file not found"
**Solution**: Make sure you're running the notebook from the `notebooks/` directory, or adjust the path:
```python
config = ConfigLoader('../config/config.yaml')  # Correct for notebooks/ directory
```

### Issue: "No module named 'utils.traveco_utils'"
**Solution**: Check that `sys.path.append('..')` is executed before the import:
```python
import sys
sys.path.append('..')  # This must come BEFORE the import
from utils.traveco_utils import ConfigLoader
```

### Issue: "KeyError: 'RKdNr'" or similar column errors
**Solution**: The data may have slightly different column names. Check available columns:
```python
print("Available columns:", list(df.columns))
```

Then adjust the column name in the code to match your data.

---

## Prevention

To avoid module caching issues in the future:

1. **Always restart kernel** after modifying `.py` files in `utils/`
2. Use **"Restart & Run All"** instead of running cells individually
3. Keep one terminal/console open with the notebook to see import errors clearly

---

## Still Having Issues?

If the problem persists:

1. Check Python version: Should be 3.10+
   ```bash
   python --version
   ```

2. Verify file exists and has the method:
   ```bash
   grep -n "def map_customer_divisions" utils/traveco_utils.py
   ```
   Should show line 339

3. Check for syntax errors in traveco_utils.py:
   ```python
   python -m py_compile utils/traveco_utils.py
   ```

4. Review `IMPLEMENTATION_SUMMARY.md` for complete list of changes

---

## Quick Reference: Execution Order

Correct order for running updated notebooks:

```
1. Restart Kernel
2. Run All cells in notebook 02 (data cleaning)
3. Restart Kernel
4. Run All cells in notebook 03 (feature engineering) ← You are here
5. Restart Kernel
6. Run All cells in notebook 04 (aggregation)
7. Run notebook 06 (tour cost analysis)
```

**Tip**: Restarting kernel between notebooks ensures clean state and fresh imports!
