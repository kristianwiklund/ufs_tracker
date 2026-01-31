# Notices to Mariners (UFS) - Severity Levels and Types

**Version**: 1.0  
**Date**: 2026-01-29  
**Language**: English  
**Source**: Based on UKHO Admiralty and Swedish Maritime Administration standards

---

## 📋 Overview

UFS Tracker classifies notices into **three main categories** based on their duration and nature. Each type has different handling requirements and visual markings.

---

## 🟢 Permanent Notices (Permanent Corrections)

### Definition

**Permanent notices** are changes that must be applied permanently to the nautical chart and remain in effect until superseded or until a new chart edition is issued.

### Visual Marking

**Badge**: 🟢 (Green circle)  
**Paper chart marking**: Magenta ink (0.18-0.25mm pen)  
**Erasable**: NO - Permanent marking

### Criteria

Permanent notices are issued for:

✅ **Permanent physical changes**:
- New lighthouse or navigation mark installed
- Depth changed (dredging, shoaling)
- Harbor facilities built/demolished
- Bridges constructed
- Cables or pipelines laid
- Wreck stabilized or removed permanently

✅ **Administrative changes**:
- Updated maritime traffic regulations
- New fairway systems
- Changed traffic separation schemes
- Updated light characteristics (permanent change)

✅ **Cartographic corrections**:
- Corrected depth contours
- Name changes (official)
- Position corrections (chart errors)

### Handling

**Application**:
1. Mark change on chart with **magenta ink**
2. Write notice number in lower left corner of chart
3. Record in correction log (NP133A style)
4. Mark as "Implemented" in UFS Tracker

**Removal**:
- NEVER removed (except with new chart edition)
- Counts toward 6-correction limit
- Remains until chart is replaced

**Priority**: Normal (unless specifically marked urgent)

---

## 🔴 Temporary Notices (T)

### Definition

**Temporary notices** (marked with "T") are changes that only apply for a **limited time period**. They must be removed when the validity period expires.

### Visual Marking

**Badge**: 🔴 T (Red circle with "T")  
**Paper chart marking**: PENCIL (erasable!)  
**Erasable**: YES - MUST be erased after expiry

**If expired**:  
**Badge**: 🔴 T (Expired) (Strikethrough, gray)

### Criteria

Temporary notices are issued for:

✅ **Time-limited works**:
- Dredging in progress (temporary obstruction)
- Construction work at sea
- Cable or pipe laying
- Blasting operations
- Salvage operations

✅ **Temporary navigation hazards**:
- Temporary buoys placed
- Wreck to be salvaged soon
- Temporary anchoring prohibitions
- Exercise areas (limited time)
- Firing practice (specific dates)

✅ **Temporary light changes**:
- Light extinguished for maintenance
- Temporary light installed
- Light character changed temporarily

✅ **Weather-dependent changes**:
- Ice NOTAM (seasonal)
- Flood warnings
- Extremely low water

### Validity Period

The notice typically contains:
- **Start date**: "From 2024-06-15"
- **End date**: "Until 2024-09-30"
- **Or**: "Until further notice" (but still temporary)

**Examples from UFS**:
> "Valid until 2024-12-31"  
> "During period 1 June - 31 August"  
> "Until further notice"

### Handling

**Application**:
1. Mark change with **PENCIL** (not ink!)
2. Note expiry date clearly
3. File notice separately (T&P folder)
4. Set reminder for expiry date
5. Mark in UFS Tracker with expiry date note

**Removal**:
1. When expiry date passed: **ERASE** the marking
2. Remove from T&P archive
3. Mark as "Expired" in UFS Tracker
4. Does NOT count toward 6-correction limit (after removal)

**Important**: Don't forget to erase! Old T-notices can cause navigation errors.

**Priority**: HIGH - May affect immediate navigation

---

## 🟡 Preliminary Notices (P)

### Definition

**Preliminary notices** (marked with "P") are **quick warnings** based on incomplete information. They are later replaced by a permanent notice when a full survey is complete.

### Visual Marking

**Badge**: 🟡 P (Yellow circle with "P")  
**Paper chart marking**: PENCIL (erasable!)  
**Erasable**: YES - Erased when permanent version arrives

### Criteria

Preliminary notices are issued for:

✅ **Unverified information**:
- Reported shoal area (not surveyed)
- Suspected wreck
- Reported obstruction
- Potential navigation hazard

✅ **Incomplete measurements**:
- Quick depth sounding (not official survey)
- Preliminary position (GPS note from vessel)
- Estimated height/depth

✅ **Urgent safety warnings**:
- Newly discovered danger requiring immediate warning
- Serious hazard where full survey takes time
- Quick warning before complete details available

### Lifecycle

```
1. Preliminary Notice (P) issued
   ↓
2. Survey conducted
   ↓
3. Permanent Notice replaces P-notice
   ↓
4. P-marking erased, permanent marking applied
```

**Example**:
- **P-Notice 18370P**: "Reported shoal area, depth unknown"
- **Replaced by Notice 18400**: "Shoal confirmed, depth 3.2m at position..."

### Handling

**Application**:
1. Mark with **PENCIL** (erasable)
2. Mark clearly "P" next to it
3. File in T&P folder
4. **Monitor** for replacing permanent notice
5. Mark in UFS Tracker as preliminary

**Replacement**:
1. When permanent notice arrives: **ERASE** P-marking
2. Apply permanent marking in magenta
3. Note in log that P was replaced by permanent
4. Remove P from T&P archive
5. Update in UFS Tracker (link to replacing notice)

**Priority**: VERY HIGH - Safety warnings requiring immediate attention

---

## 📊 Summary of Differences

| Aspect | 🟢 Permanent | 🔴 Temporary (T) | 🟡 Preliminary (P) |
|--------|--------------|------------------|-------------------|
| **Duration** | Until superseded | Limited time | Temporary (replaced) |
| **Marking** | Magenta ink | Pencil | Pencil |
| **Erasable** | NO | YES (at expiry) | YES (at replacement) |
| **Filing** | Permanent | T&P folder | T&P folder |
| **Counts to 6-limit** | YES | NO (after erasure) | NO (after erasure) |
| **Expiry date** | None | Yes, specific | When replacement comes |
| **Priority** | Normal | High | Very high |
| **Example** | New lighthouse | Dredging ongoing | Reported wreck |

---

## 🎯 Why This Matters

### Safety

**Incorrect handling can lead to**:
- Navigation hazards not marked
- Old warnings causing confusion (unerased T-notices)
- Overlooked safety risks (unimplemented P-notices)

### Correct Charts

**Proper handling provides**:
- ✅ Up-to-date charts
- ✅ Accurate information
- ✅ Safe navigation
- ✅ Inspection-ready documentation

### Legal Requirements

For **commercial vessels**:
- Requirement for updated charts
- PSC inspections check correction logs
- Must show all notices handled
- T&P notices must be properly filed

---

## 🔍 How to Identify the Type

### In UFS Database

**Number format**:
- `18369` = Permanent (no suffix)
- `18370T` = Temporary (T suffix)
- `18371P` = Preliminary (P suffix)

### In UFS Tracker

**Visual indicators**:
- 🟢 = Permanent
- 🔴 T = Temporary
- 🟡 P = Preliminary
- 🔴 T (Expired) = Expired temporary (should be erased)

### In Notice Title

**Keywords for Temporary (T)**:
- "Temporary"
- "During period"
- "Until further notice"
- "Valid until [date]"
- "During construction"
- "Works in progress"

**Keywords for Preliminary (P)**:
- "Preliminary"
- "Reported"
- "Unconfirmed"
- "Position approximate"
- "Depth uncertain"
- "Subject to confirmation"

---

## 📝 Practical Examples

### Example 1: Permanent Notice

**Notice 18500**  
**Title**: "Stockholm. New leading line established"  
**Type**: 🟢 Permanent  
**Action**:
1. Mark new leading line with magenta ink
2. Write "18500" in lower left corner
3. Record in correction log
4. Mark as implemented in UFS Tracker
5. **NEVER erase**

---

### Example 2: Temporary Notice

**Notice 18501T**  
**Title**: "Dredging in Karlskrona harbor. Valid until 2024-09-30"  
**Type**: 🔴 T (Temporary)  
**Action**:
1. Mark dredging area with PENCIL
2. Write "18501T" and "Expires 2024-09-30"
3. File notice in T&P folder
4. Mark in UFS Tracker with expiry date
5. **2024-10-01**: ERASE marking
6. Remove from T&P archive

---

### Example 3: Preliminary Notice

**Notice 18502P**  
**Title**: "Reported shoal area east of Sandhamn. Position approximate"  
**Type**: 🟡 P (Preliminary)  
**Action**:
1. Mark area with PENCIL
2. Write "18502P" and "PRELIMINARY"
3. File in T&P folder
4. Mark in UFS Tracker as preliminary
5. **Monitor** UFS for replacing notice
6. When **Notice 18550** arrives (permanent):
   - ERASE "18502P" marking
   - Mark with magenta per 18550
   - Link in UFS Tracker: "18502P replaced by 18550"

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Marking T-notice in Magenta
**Problem**: Cannot be erased later  
**Correct**: ALWAYS use pencil for T and P

### ❌ Mistake 2: Forgetting to Erase Expired T-Notices
**Problem**: Old warnings confuse, incorrect information  
**Correct**: Set reminders, check regularly

### ❌ Mistake 3: Not Monitoring P-Notices
**Problem**: Miss permanent replacement  
**Correct**: Monitor UFS for follow-up

### ❌ Mistake 4: Counting T/P Toward 6-Limit
**Problem**: Replace charts unnecessarily  
**Correct**: Only permanent count (after T/P erased)

---

## 🛠️ Usage in UFS Tracker

### Automatic Identification

UFS Tracker automatically identifies notice type from number:
- Suffix "T" → Temporary
- Suffix "P" → Preliminary
- No suffix → Permanent

### Expiry Tracking

For temporary notices:
- Tracker attempts to extract expiry date from title/content
- Shows warning when expiry date approaches
- Marks as "Expired" after date

### Replacement Links

For preliminary notices:
- Tracker can link to replacing permanent notice
- Shows history: "P18502 → 18550"
- Helps track updates

---

## 📚 References

### International Standards
- **UKHO NP294**: "Admiralty Guide to the Practical Use of Charts"
- **UKHO NP133A**: "Chart Correction Log and Folio Index"
- **IALA**: Recommendations on Marine Signal Stations
- **IMO**: International Maritime Organization Guidelines

### Swedish Sources
- **Sjöfartsverket**: https://ufs.sjofartsverket.se
- **Maritime traffic regulations**: SJÖFS regulations
- **Swedish Cruising Association**: Small craft chart guidelines

---

## 📞 Support

If you're unsure about:
- Notice type
- How to handle a notice
- Expiry date interpretation
- Replacement notices

**Contact**:
- Swedish Maritime Administration: https://www.sjofartsverket.se
- UFS Tracker GitHub: https://github.com/kristianwiklund/ufs_tracker/issues

---

**Important**: This is a guide for **hobby and recreational use**. For **commercial shipping**, complete SOLAS and STCW requirements must be followed, including official certification and inspection of correction procedures.

**Last updated**: 2026-01-29  
**Version**: 1.0  
**Language**: English
