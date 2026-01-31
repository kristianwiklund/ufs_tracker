# Critical Fix: Chart Mapping Bug (Issue #2)

**Date**: 2026-01-29  
**Issue**: Wrong notices returned for chart "10"  
**Status**: ✅ FIXED

---

## 🔍 Root Cause Analysis

### The Problem

When searching for chart "10", the system returned notices for completely different charts (e.g., 15841, 16438).

### Debug Output

```
Searching for sjökort: '10'
Mapped to ID: '10'              ← BUG: Using input directly!
Total sjökort available: 117
Direct match found: 4735        ← This is the CORRECT ID!
```

### The Bug

**File**: `services/scraper.py`  
**Function**: `get_chart_id()`  
**Line**: 98-99

**Buggy Code**:
```python
def get_chart_id(chart_name, chart_map):
    # ...
    
    # If it's already a number, return it
    if str(chart_name).isdigit():
        return str(chart_name)  # ← BUG: Returns "10" instead of "4735"
    
    # Try exact match
    if chart_name in chart_map:
        return chart_map[chart_name]  # ← This never executes for numbers!
```

**Problem**: The function checked if input was a digit BEFORE checking the map, so numeric chart names never got looked up!

---

## ✅ The Fix

**New Logic Order**:
1. ✅ Try exact match in map FIRST (even for numbers)
2. ✅ Try case-insensitive match
3. ⚠️ Use as-is only as fallback (with warning)

**Fixed Code**:
```python
def get_chart_id(chart_name, chart_map):
    """Map chart name to its ID using the provided mapping"""
    if not chart_name:
        return None
    
    chart_name_str = str(chart_name)
    
    # Try exact match first (even for numbers)
    if chart_name_str in chart_map:
        return chart_map[chart_name_str]  # ← Now this runs FIRST!
    
    # Try case-insensitive match
    for name, chart_id in chart_map.items():
        if name.lower() == chart_name_str.lower():
            return chart_id
    
    # If it's a number and no match found, try it as-is (fallback)
    if chart_name_str.isdigit():
        debug_print(f"WARNING: No mapping found for '{chart_name_str}', using as direct ID")
        return chart_name_str
    
    # Return as-is if no match (last resort)
    debug_print(f"WARNING: No mapping found for '{chart_name_str}', using as-is")
    return chart_name_str
```

---

## 📊 Before vs After

### Before (Buggy)

```
Input: "10"
Check: Is it a digit? YES
Return: "10"
Result: Searches UFS for ID "10" (wrong chart!)
Notices: 15841, 16438 (not related to chart 10)
```

### After (Fixed)

```
Input: "10"
Check: Is "10" in chart_map? YES → maps to "4735"
Return: "4735"
Result: Searches UFS for ID "4735" (correct chart!)
Notices: Correct notices for chart 10
```

---

## 🧪 Testing

### Test Case 1: Chart "10"

**Before**:
```bash
python app.py --debug
# Search for "10"
# Result: Wrong notices (15841, 16438, etc.)
```

**After**:
```bash
python app.py --debug
# Search for "10"
# Debug shows: "Mapped to ID: '4735'"
# Result: Correct notices for chart 10!
```

### Test Case 2: Other Numeric Charts

Test with various chart numbers to ensure mapping works:
- "111" → Should map correctly
- "621" → Should map correctly
- "54" → Should map correctly

### Test Case 3: Text Charts (Should Still Work)

Test with båtsportkort names:
- "Bsp Stockholm N 2024" → Should still work
- "Bsp Mälaren - Hjälmaren 2024" → Should still work

---

## 🎯 Impact

### Charts Affected

This bug affected **ALL numeric chart names**, including:
- Single-digit charts: 1-9
- Double-digit charts: 10-99
- Triple-digit charts: 100-999

**Estimated**: ~117 sjökort potentially affected (all numeric ones)

### Data Integrity

**Important**: Existing database data may contain wrong notices!

**Recommended Actions**:
1. ✅ Apply this fix
2. ⚠️ Consider re-scraping charts that were searched with numeric names
3. ⚠️ Check if any notices are associated with wrong charts
4. ⚠️ May need to clean up database

**Database Cleanup Script** (if needed):
```python
# Optional: Clear notices for charts that were incorrectly scraped
# Only run if you've had searches with wrong results

def cleanup_wrong_notices():
    conn = get_db()
    c = conn.cursor()
    
    # Get all numeric chart identifiers
    c.execute('''
        SELECT DISTINCT chart_identifier 
        FROM implementation_status 
        WHERE chart_identifier GLOB '[0-9]*'
    ''')
    
    numeric_charts = [row['chart_identifier'] for row in c.fetchall()]
    
    print(f"Found {len(numeric_charts)} numeric chart identifiers")
    print("These may have wrong notices. Consider re-scraping:")
    for chart in numeric_charts:
        print(f"  - Chart {chart}")
    
    conn.close()

# Run this to see which charts might need re-scraping
# cleanup_wrong_notices()
```

---

## 📝 Additional Improvements

The fix also adds **better logging**:

```python
# Now warns when using fallback
debug_print(f"WARNING: No mapping found for '{chart_name_str}', using as direct ID")
```

This helps catch:
- Charts not in the mapping (new charts added to UFS)
- Typos in chart names
- Mapping cache issues

---

## ✅ Verification

### How to Verify Fix Works

1. **Run in debug mode**:
   ```bash
   python app.py --debug
   ```

2. **Search for chart "10"**

3. **Check debug output**:
   ```
   Searching for sjökort: '10'
   Mapped to ID: '4735'  ← Should be 4735, not 10!
   ```

4. **Check notices returned**:
   - Should be relevant to chart 10
   - Should NOT be notices like 15841, 16438

5. **Search for other numeric charts**:
   - Try "111", "621", "54"
   - All should map to correct IDs

---

## 🔄 Rollback

If this fix causes issues:

```bash
# Revert to original version
git checkout services/scraper.py

# Or manually change line 98-99 back to:
if str(chart_name).isdigit():
    return str(chart_name)
```

---

## 📊 Summary

| Aspect | Before | After |
|--------|--------|-------|
| Chart "10" maps to | "10" (wrong) | "4735" (correct) |
| Notices for chart 10 | Wrong notices | Correct notices |
| Numeric charts work | ❌ No | ✅ Yes |
| Text charts work | ✅ Yes | ✅ Yes |
| Warnings on fallback | ❌ No | ✅ Yes |

---

## 🎓 Lessons Learned

1. **Order matters**: Check mappings BEFORE assuming input is correct
2. **Validate assumptions**: Just because it's a number doesn't mean it's an ID
3. **Debug output is essential**: Without it, we'd never have found this
4. **Test edge cases**: Single-digit, double-digit, triple-digit charts all behave differently

---

**Status**: ✅ Fixed and Ready for Testing  
**Priority**: CRITICAL - This affected core functionality  
**Risk**: LOW - Fix is simple and logical  
**Testing Required**: YES - Verify with real searches

