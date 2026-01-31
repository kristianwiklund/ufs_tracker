# Notice Type Severity Levels - User Guide

**Document Version**: 1.0  
**Date**: 2026-01-29  
**For**: UFS Maritime Notices Tracker Users  
**Based on**: UKHO Admiralty Standards (NP294, NP133A)

---

## 🎯 Purpose of This Guide

This document explains the **three types of maritime notices** and their severity levels, helping you understand which corrections must be applied immediately and which can wait.

---

## 📋 Notice Type Overview

UFS Maritime Notices are classified into **three severity levels**, indicated by colored badges in the application:

| Badge | Type | Severity | Urgency |
|-------|------|----------|---------|
| 🟢 | **Permanent** | Standard | Apply before next voyage |
| 🟡 **P** | **Preliminary** | Medium | Apply now, verify later |
| 🔴 **T** | **Temporary** | Varies | Apply immediately, remove when expired |

---

## 🟢 PERMANENT Corrections (Green Badge)

### What Are They?

**Permanent corrections** are standard chart updates based on:
- Verified survey data
- Confirmed changes to navigation aids
- Updated depth soundings
- New or removed navigational features
- Chart edition updates

### How to Identify

- Notice number has **no suffix** (e.g., "18369")
- Green badge: 🟢
- No expiry date

### Severity Level: STANDARD

**Priority**: Apply before next voyage to affected area  
**Method**: Magenta ink (in this app: mark as "Implemented")  
**Permanence**: Remains until new chart edition

### Examples

```
Notice #18369 🟢
"New lighthouse established at position 59°20.5'N 018°05.2'E"

Action: Add lighthouse symbol to chart in magenta
When: Before next voyage through this area
Permanent: Yes - remains on chart until replaced
```

```
Notice #19761 🟢
"Depth reduced to 8.2m in position 56°10.3'N 015°35.8'E"

Action: Update depth sounding on chart
When: Before navigating this area
Critical: YES - affects safe navigation depth
```

### Criteria for STANDARD Severity

✅ Based on verified survey  
✅ Confirmed and validated  
✅ Will not change short-term  
✅ No time limit  
✅ Affects future voyages

### User Actions Required

1. ✅ Review notice details
2. ✅ Apply correction to chart(s) in magenta ink
3. ✅ Mark notice as "Implemented" in UFS Tracker
4. ✅ Record in correction log (NP133A)
5. ✅ Update "corrected up to" number

---

## 🟡 PRELIMINARY Corrections (Yellow Badge - P)

### What Are They?

**Preliminary notices** (P) are issued when:
- Survey data is incomplete but hazard is known
- Quick notification needed before full survey
- Awaiting verification or confirmation
- Temporary information pending permanent notice

### How to Identify

- Notice number ends with **"P"** (e.g., "18370P")
- Yellow badge: 🟡 **P**
- Usually followed by permanent notice later

### Severity Level: MEDIUM (Precautionary)

**Priority**: Apply immediately as precaution  
**Method**: **Pencil** (erasable - not magenta!)  
**Permanence**: Temporary - will be replaced

### Why Different Treatment?

Preliminary notices are:
- ⚠️ **Unverified** - based on reports, not full survey
- ⚠️ **Incomplete** - may lack exact details
- ⚠️ **Subject to change** - details may be corrected
- ⚠️ **Precautionary** - "better safe than sorry"

### Examples

```
Notice #18370P 🟡 P
"Reported obstruction in approximate position 58°15'N 016°45'E"

Action: Mark approximate danger area on chart in PENCIL
When: IMMEDIATELY before next voyage
Why pencil: Position may be refined in permanent notice
Wait for: Permanent notice with exact position
```

```
Notice #15850P 🟡 P
"Unlit buoy reported missing, position 59°45.2'N 019°12.1'E"

Action: Cross out buoy symbol in PENCIL
When: Immediately
Why pencil: May be replaced or position corrected
Expected: Permanent notice when buoy is re-established
```

### Criteria for MEDIUM Severity

⚠️ Unverified information  
⚠️ Approximate positions  
⚠️ Pending full survey  
⚠️ Will be superseded  
⚠️ Apply as precaution

### User Actions Required

1. ⚠️ Review notice details carefully
2. ⚠️ Apply correction in **PENCIL** (not magenta!)
3. ⚠️ Mark as "Implemented" in UFS Tracker
4. ⚠️ Note in correction log as "Preliminary"
5. ⏳ **Watch for permanent notice** to replace it
6. ✏️ Update with permanent correction when issued
7. 🗑️ Erase pencil marks when applying permanent

### Special Handling in UFS Tracker

The application helps you track preliminary notices:
- Yellow badge makes them stand out
- Can filter to show only preliminary notices
- Note field to record when permanent notice arrives
- Track when preliminary was superseded

---

## 🔴 TEMPORARY Corrections (Red Badge - T)

### What Are They?

**Temporary notices** (T) are issued for:
- Short-term hazards (construction, exercises)
- Time-limited changes
- Seasonal restrictions
- Temporary navigational changes
- Events with known end dates

### How to Identify

- Notice number ends with **"T"** (e.g., "18371T")
- Red badge: 🔴 **T**
- **Has expiry date** or time period
- Often includes "valid until" or "from ... to ..."

### Severity Level: TIME-CRITICAL (Urgent)

**Priority**: Apply **IMMEDIATELY**  
**Method**: **Pencil** (must be erasable for removal)  
**Permanence**: **Remove when expired**

### Why URGENT?

Temporary notices often indicate:
- 🚨 **Active hazards** - ongoing now
- 🚨 **Immediate danger** - affects current voyages
- 🚨 **Time-sensitive** - may expire soon
- 🚨 **Dynamic situation** - can change quickly

### Examples

```
Notice #18371T 🔴 T
"Firing exercise area active 01-15 July 2024
 Area bounded by: 59°00'N 017°30'E, 59°05'N 017°35'E,
                  59°05'N 017°40'E, 59°00'N 017°35'E
 Mariners advised to keep clear"

Action: Mark danger area on chart in PENCIL
When: IMMEDIATELY if sailing in July 2024
Expires: 15 July 2024
Remove: Erase pencil marks after 15 July 2024
```

```
Notice #19500T 🔴 T
"Pipeline laying operations 10-25 March 2024
 Position: 58°30'N 016°20'E to 58°35'N 016°30'E
 Obstruction with buoys marking route
 Valid: 10-25 March 2024"

Action: Draw pipeline route in PENCIL
When: IMMEDIATELY
Expires: 25 March 2024
Critical: YES - physical obstruction
Remove: Erase after 25 March 2024
```

```
Notice #17650T 🔴 T (Expired Example)
"Temporary light buoy, valid until further notice
 Last updated: 2023-06-15"

Status in App: 🔴 T (Utgången) - Expired
Action: Check if still valid, likely expired
Remove: Erase if confirmed expired
```

### Criteria for TIME-CRITICAL Severity

🚨 Active NOW or soon  
🚨 Time-limited duration  
🚨 Must be removed after expiry  
🚨 Dynamic situation  
🚨 Often higher risk

### User Actions Required

1. 🚨 Review notice **immediately**
2. ✏️ Apply correction in **PENCIL** (erasable!)
3. ✅ Mark as "Implemented" in UFS Tracker
4. 📅 **Note expiry date** in correction log
5. ⏰ **Set reminder** for expiry date
6. 📋 File notice separately (T notices kept separate)
7. 🗑️ **Remove correction** when expired (erase pencil)
8. ✅ Update UFS Tracker when removed

### Special Handling in UFS Tracker

The application helps manage temporary notices:
- Red badge indicates urgency
- Expiry date displayed (when found)
- "Expired" status shown: 🔴 T (Utgången)
- Can filter to show expiring notices
- Reminder field for removal date
- Track when notice was removed

### Expiry Date Detection

The UFS Tracker attempts to automatically extract expiry dates from:
- "Valid until YYYY-MM-DD"
- "Gäller till DD/MM YYYY"
- "From DD MMM to DD MMM YYYY"
- Date patterns in title or content

**Note**: Not all temporary notices have clear expiry dates. Some say "until further notice" - monitor for cancellation notices.

---

## 📊 Severity Comparison Table

| Aspect | Permanent 🟢 | Preliminary 🟡 P | Temporary 🔴 T |
|--------|--------------|------------------|----------------|
| **Urgency** | Before next voyage | Immediate precaution | IMMEDIATE |
| **Ink/Pencil** | Magenta (permanent) | Pencil (erasable) | Pencil (erasable) |
| **Verification** | Fully verified | Unverified/partial | Verified but time-limited |
| **Duration** | Permanent | Until superseded | Until expiry date |
| **Action** | Apply and keep | Apply, watch for update | Apply, then remove |
| **Log Entry** | Standard entry | Note as "Preliminary" | Note expiry date |
| **Priority** | Standard | Medium | High/Urgent |
| **Superseded** | New edition only | Permanent notice | Expiry or cancellation |
| **Filing** | With chart | With chart | Separate T file |

---

## 🎯 Workflow by Severity

### Permanent Notice Workflow 🟢

```
1. Receive Notice #18369 🟢
2. Identify affected charts
3. Apply in MAGENTA ink
4. Mark "Implemented" in UFS Tracker
5. Log in NP133A
6. Update "corrected up to" number
7. File with chart
8. DONE - remains permanently
```

### Preliminary Notice Workflow 🟡 P

```
1. Receive Notice #18370P 🟡 P
2. Identify affected charts
3. Apply in PENCIL (not magenta!)
4. Mark "Implemented" in UFS Tracker
5. Log as "Preliminary" in NP133A
6. Watch for permanent notice
   ↓
7. Receive permanent notice #18400 🟢
8. ERASE pencil marks
9. Apply permanent in MAGENTA
10. Update tracker - both notices
11. Note in log: "P superseded by #18400"
```

### Temporary Notice Workflow 🔴 T

```
1. Receive Notice #18371T 🔴 T "Valid 01-15 July"
2. Identify affected charts
3. Apply IMMEDIATELY in PENCIL
4. Mark "Implemented" in UFS Tracker
5. NOTE EXPIRY DATE: 15 July
6. Log with expiry date in NP133A
7. File in separate T notices file
8. SET REMINDER for 15 July
   ↓
9. On 16 July: ERASE pencil marks
10. Mark as "Removed" in tracker
11. Note in log: "T removed - expired"
12. Move notice to "expired T" file
```

---

## 🛡️ Safety Considerations

### Critical Safety Rule

**ALWAYS apply corrections before voyages to affected areas**, regardless of type:

- 🟢 Permanent: Apply before navigating area
- 🟡 P Preliminary: Apply as precaution before navigating
- 🔴 T Temporary: Apply IMMEDIATELY if active now

### Risk Assessment

When deciding urgency, consider:

1. **Does it affect my planned route?**
   - If YES → Apply immediately
   - If NO → Apply before next voyage to that area

2. **Is it a safety hazard?**
   - Depth change → HIGH PRIORITY
   - New obstruction → HIGH PRIORITY
   - Light characteristic change → HIGH PRIORITY
   - Administrative change → Lower priority

3. **Is it temporary and active now?**
   - 🔴 T active → IMMEDIATE
   - 🔴 T future → Apply before start date
   - 🔴 T expired → May ignore (verify first)

4. **Is it preliminary?**
   - 🟡 P → Apply as precaution
   - Watch for permanent update
   - Treat as if permanent until verified

---

## 📝 Best Practices

### For Permanent Notices 🟢

✅ Apply in magenta ink (permanent marker)  
✅ Mark neatly and clearly  
✅ Use standard symbols  
✅ Record in correction log  
✅ Update "corrected up to" number  
✅ Check after 6 corrections (may need new chart)

### For Preliminary Notices 🟡 P

✅ Apply in **pencil** (must be erasable)  
✅ Mark "P" near correction  
✅ Note as preliminary in log  
✅ File separately or mark clearly  
✅ **Check weekly** for permanent notice  
✅ Update when permanent issued  
✅ Erase and replace with magenta

### For Temporary Notices 🔴 T

✅ Apply in **pencil** (must be erasable)  
✅ Mark "T" and expiry date near correction  
✅ Note expiry date in log  
✅ **File in separate T folder**  
✅ Set calendar reminder for expiry  
✅ **Check weekly** for cancellations  
✅ **Remove promptly** when expired  
✅ Do NOT convert to magenta (temporary only!)

---

## 🔍 Common Questions

### Q: Can I skip preliminary notices if I wait for permanent?

**A: NO.** Preliminary notices are issued because:
- Hazard exists NOW
- Waiting for permanent could be dangerous
- Better safe than sorry
- Permanent might take weeks/months

### Q: What if temporary notice has no expiry date?

**A:** 
- Apply it anyway (active until cancelled)
- Check UFS weekly for cancellation notice
- Contact UFS if unclear
- Mark in tracker as "until further notice"

### Q: Do I need to track all three types?

**A: YES.** All notices affect chart safety:
- Permanent = standard updates
- Preliminary = unverified hazards (still real)
- Temporary = active hazards (time-limited)

### Q: How do I know when preliminary becomes permanent?

**A:**
- Check UFS weekly
- Permanent notice will reference preliminary
- Usually same area/feature
- Notice number will be higher, no "P" suffix

### Q: Can temporary notices become permanent?

**A:**
- Rarely - different purposes
- If hazard becomes permanent, new permanent notice issued
- Original T notice expires/cancelled
- Apply new permanent notice separately

### Q: What happens if I miss a temporary notice expiry?

**A:**
- Erase as soon as you notice
- Check if extension issued
- Log the removal
- Not critical (hazard no longer exists)

---

## 🎓 Learning the System

### For New Users

Start with this priority:
1. **Learn permanent** (🟢) - most common, standard process
2. **Learn temporary** (🔴 T) - more urgent, must track expiry
3. **Learn preliminary** (🟡 P) - less common, watch for updates

### Practice Workflow

1. Search for your charts in UFS Tracker
2. Note the badge colors
3. Sort by notice type
4. Apply permanent first (🟢)
5. Then urgent temporary (🔴 T active now)
6. Then preliminary as precaution (🟡 P)
7. Set reminders for T expiry dates

---

## 📚 References

This severity classification is based on:

- **UKHO NP294** - Admiralty Guide to the Practical Use of ENCs
- **UKHO NP133A** - Chart Correction Log and Notices Received Book
- **IALA** - International Association of Marine Aids to Navigation and Lighthouse Authorities
- **IMO** - International Maritime Organization guidelines
- **Swedish Maritime Administration** - UFS system documentation

---

## 🆘 When in Doubt

**Safety First Rule:**
- If unsure about severity → **Treat as higher severity**
- If unsure about type → **Apply immediately in pencil**
- If unsure about expiry → **Keep until confirmed expired**
- If unsure about anything → **Contact Swedish Maritime Administration**

**UFS Contact:**
- Website: https://ufs.sjofartsverket.se
- Email: [Check UFS website for current contact]

---

## ✅ Quick Reference Card

```
🟢 PERMANENT
├─ Apply: Before next voyage
├─ Method: Magenta ink
├─ Keep: Until new edition
└─ Example: New lighthouse

🟡 P PRELIMINARY  
├─ Apply: Immediately (precaution)
├─ Method: PENCIL (erasable)
├─ Keep: Until permanent notice
└─ Example: Reported obstruction

🔴 T TEMPORARY
├─ Apply: IMMEDIATELY
├─ Method: PENCIL (erasable)
├─ Keep: Until expiry date
├─ Remove: Erase when expired
└─ Example: Firing exercise
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-29  
**Status**: Active

**Remember**: When in doubt, err on the side of caution. Your safety depends on having accurate, up-to-date charts!

⚓ Safe Navigation! 📊
