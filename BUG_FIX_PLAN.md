# UFS Tracker Bug Fixes - Implementation Plan

**Date**: 2026-01-29  
**Priority**: CRITICAL (Performance) → HIGH (Wrong notices) → MEDIUM (Cosmetic)

---

## BUGS IDENTIFIED

### 🔴 CRITICAL - Issue #3: Performance (Infinite Loop)
**Symptom**: `/get_tracked_charts` called multiple times per second, Firefox hangs  
**Root Cause**: 
- Line 210 in notices.html: `span.innerHTML = makeAffectedChartsClickable(affectedChartsText, trackedChartsList);`
- This calls the function `makeAffectedChartsClickable()` which is ASYNC
- Returns a Promise instead of HTML string
- The function name conflicts with the function being defined

**Fix**: Rename the utility function and make it sync

### 🔴 CRITICAL - Issue #2: Wrong Notices Downloaded
**Symptom**: Searching for chart "10" returns wrong notices (15841, 16438)  
**Root Cause**: Likely chart ID mapping issue - "10" might map to wrong ID  
**Fix**: Add logging to scraper, verify chart mapping

### 🟡 HIGH - Issue #4: Affected Charts Display
**Symptom**: Shows "[object Promise]" or non-clickable charts  
**Root Cause**: Same as Issue #3 - async/sync mismatch  
**Fix**: Same as Issue #3

### 🟡 HIGH - Issue #5: Firefox Console Error
**Symptom**: Error about "make charts clickable"  
**Root Cause**: Same as Issue #3  
**Fix**: Same as Issue #3

### 🟡 HIGH - Issue #6: Syntax Error in common.js:107
**Symptom**: `Uncaught SyntaxError: missing ) after formal parameters`  
**Root Cause**: Line 107: `function getNoticeTypeBadge(noticeType, expiry Date = null)`  
Should be: `function getNoticeTypeBadge(noticeType, expiryDate = null)` (no space)  
**Fix**: Remove space in parameter name

### 🟢 MEDIUM - Issue #1: Visual Separation
**Symptom**: Hard to distinguish between notices  
**Root Cause**: All notice cards look similar  
**Fix**: Add alternating background colors, better borders

---

## STAGED FIX APPROACH

### Stage 1: CRITICAL Performance Fix (Do First)

**Files to Fix**:
1. `static/js/common.js` - Fix syntax error
2. `templates/notices.html` - Fix infinite loop

**Changes**:

#### Fix 1: common.js line 107
```javascript
// WRONG:
function getNoticeTypeBadge(noticeType, expiry Date = null) {

// CORRECT:
function getNoticeTypeBadge(noticeType, expiryDate = null) {
```

#### Fix 2: Rename function in common.js
```javascript
// RENAME THIS FUNCTION (it conflicts with async function)
function processAffectedChartsHTML(affectedChartsText, trackedCharts) {
    // ... existing code ...
}
```

#### Fix 3: notices.html - Fix the call
```javascript
// WRONG (line 210):
span.innerHTML = makeAffectedChartsClickable(affectedChartsText, trackedChartsList);

// CORRECT:
span.innerHTML = processAffectedChartsHTML(affectedChartsText, trackedChartsList);
```

#### Fix 4: Make processAffectedChartsHTML synchronous
```javascript
// Remove all async/await, make it pure string manipulation
function processAffectedChartsHTML(affectedChartsText, trackedCharts) {
    const chartRefs = affectedChartsText.split(',').map(s => s.trim()).filter(s => s);
    const results = [];
    
    chartRefs.forEach(chartRef => {
        // ... process each chart ...
        results.push(createChartElementHTML(chartRef, identifier, trackedCharts));
    });
    
    return results.join(', ');
}

function createChartElementHTML(displayText, identifier, trackedCharts) {
    const isTracked = trackedCharts.includes(identifier);
    
    if (isTracked) {
        return `<a href="#" class="chart-link" ...>${escapeHtml(displayText)}</a>`;
    } else {
        return `<span class="chart-not-tracked">${escapeHtml(displayText)}</span>`;
    }
}
```

### Stage 2: HIGH Wrong Notices Fix

**Root Cause Analysis Needed**:
- Check what chart ID "10" maps to
- Add debug logging to scraper

**Files to Fix**:
1. `services/scraper.py` - Add logging
2. `app.py` - Add debug output

**Changes**:

#### Fix 1: Add debug logging to scraper
```python
def scrape_ufs_notices(sjokort_nummer=None, batsportkort=None, max_rows=500):
    # ... existing code ...
    
    # Add logging
    if sjokort_nummer:
        chart_id = get_chart_id(sjokort_nummer, sjokort_map)
        debug_print(f"Searching for sjökort: {sjokort_nummer}")
        debug_print(f"Mapped to ID: {chart_id}")
        debug_print(f"Available mappings: {sjokort_map}")
    
    # ... rest of code ...
```

#### Fix 2: Verify parameter name
Check if using `ChartNumbers` (correct) vs `Chart` (wrong)

### Stage 3: MEDIUM Visual Improvements

**Files to Fix**:
1. `static/css/main.css` - Add better visual separation

**Changes**:

#### Fix 1: Alternating notice card colors
```css
.notice-card {
    background: white;
    border-left: 4px solid #667eea;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: box-shadow 0.3s;
}

.notice-card:nth-child(even) {
    background: #f8f9fa;
}

.notice-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}
```

#### Fix 2: Better borders and spacing
```css
.notice-card {
    border: 1px solid #e0e0e0;
    margin-bottom: 25px; /* More space between cards */
}

.notice-header {
    background: linear-gradient(90deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
    padding: 10px 15px;
    margin: -20px -20px 15px -20px;
    border-radius: 5px 5px 0 0;
}
```

---

## DETAILED FIX CODE

### File 1: static/js/common.js

**Line 107** - Fix syntax error:
```javascript
// BEFORE:
function getNoticeTypeBadge(noticeType, expiry Date = null) {

// AFTER:
function getNoticeTypeBadge(noticeType, expiryDate = null) {
```

**Lines 130-200** - Rename and fix function:
```javascript
/**
 * Process affected charts and make them clickable (RENAMED from makeAffectedChartsClickable)
 */
function processAffectedChartsHTML(affectedChartsText, trackedCharts) {
    if (!affectedChartsText) return '';
    
    const chartRefs = affectedChartsText.split(',').map(s => s.trim()).filter(s => s);
    const results = [];
    
    chartRefs.forEach(chartRef => {
        // Check for concatenation
        const pageMatch = chartRef.match(/^([^\/]+)(\/.*)?$/);
        const mainPart = pageMatch ? pageMatch[1] : chartRef;
        const pageNumbers = pageMatch && pageMatch[2] ? pageMatch[2] : '';
        
        const numberBspMatch = mainPart.match(/^(\d+)(Bsp.+)$/i);
        
        if (numberBspMatch) {
            // Two charts
            const chartNumber = numberBspMatch[1];
            const bspName = numberBspMatch[2].trim();
            
            results.push(createChartElementHTML(chartNumber, chartNumber, trackedCharts));
            results.push(createChartElementHTML(bspName + pageNumbers, bspName, trackedCharts));
        } else {
            // Single chart
            const identifier = extractChartIdentifier(chartRef);
            results.push(createChartElementHTML(chartRef, identifier, trackedCharts));
        }
    });
    
    return results.join(', ');
}

/**
 * Create HTML for a chart element
 */
function createChartElementHTML(displayText, identifier, trackedCharts) {
    const isTracked = trackedCharts.includes(identifier);
    
    if (isTracked) {
        return `<a href="#" class="chart-link" title="Klicka för att visa notiser för ${escapeHtml(identifier)}" onclick="event.preventDefault(); navigateToChart('${escapeHtml(identifier)}');">${escapeHtml(displayText)}</a>`;
    } else {
        return `<span class="chart-not-tracked" title="Detta kort är inte nedladdat än">${escapeHtml(displayText)}</span>`;
    }
}
```

### File 2: templates/notices.html

**Line 210** - Fix function call:
```javascript
// BEFORE:
span.innerHTML = makeAffectedChartsClickable(affectedChartsText, trackedChartsList);

// AFTER:
span.innerHTML = processAffectedChartsHTML(affectedChartsText, trackedChartsList);
```

### File 3: static/css/main.css

**Add after existing .notice-card styles**:
```css
/* Better visual separation between notices */
.notice-card:nth-child(even) {
    background: #f8f9fa;
}

.notice-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

.notice-card {
    border: 1px solid #e0e0e0;
    margin-bottom: 25px;
}

.notice-header {
    background: linear-gradient(90deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
    padding: 10px 15px;
    margin: -20px -20px 15px -20px;
    border-radius: 5px 5px 0 0;
}

.notice-info {
    background: rgba(0,0,0,0.02);
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
```

---

## TESTING CHECKLIST

### Stage 1 Tests (Performance)
- [ ] Open notices page - should not hang Firefox
- [ ] Check browser console - no errors
- [ ] Check network tab - /get_tracked_charts called only once per page load
- [ ] Affected charts display correctly (not [object Promise])
- [ ] Affected charts are clickable

### Stage 2 Tests (Wrong Notices)
- [ ] Search for chart "10" specifically
- [ ] Verify notices returned are actually for chart 10
- [ ] Check debug output for chart ID mapping
- [ ] Search for other charts to verify they work

### Stage 3 Tests (Visual)
- [ ] Notice cards have alternating backgrounds
- [ ] Easy to distinguish between notices
- [ ] Hover effects work
- [ ] Headers have colored background
- [ ] Overall appearance is pleasant

---

## ROLLBACK PLAN

If fixes cause new issues:

1. **Performance Fix**: Can revert to old template (templates/notices_old.html)
2. **Visual Fix**: Can remove new CSS rules
3. **Scraper Fix**: Already has debug mode, can investigate further

---

## ESTIMATED TIME

- **Stage 1** (Performance): 30 minutes
- **Stage 2** (Wrong notices): 1 hour (includes investigation)
- **Stage 3** (Visual): 15 minutes

**Total**: ~2 hours

---

## PRIORITY ORDER

1. 🔴 Fix syntax error in common.js (1 minute)
2. 🔴 Fix infinite loop in notices.html (10 minutes)
3. 🔴 Test performance fix (5 minutes)
4. 🟡 Investigate wrong notices issue (30 minutes)
5. 🟡 Fix wrong notices (15 minutes)
6. 🟡 Test notice fix (10 minutes)
7. 🟢 Add visual improvements (15 minutes)
8. 🟢 Test visual improvements (5 minutes)

---

**Next Action**: Implement Stage 1 fixes immediately

