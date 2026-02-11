# Lessons Learned - Article Publisher

## Session: 2026-02-10 - Medium Table Import Failure

### Critical Errors Made

1. **Claimed work was complete without verification**
   - Ran Python script to replace HTML tables with image tags
   - Pushed to GitHub and told user it was fixed
   - **Never actually checked the resulting HTML file to verify the replacements worked**
   - User had to tell me multiple times tables were still broken before I verified

2. **Made defensive excuses instead of investigating**
   - When user reported tables still broken, made assumptions about:
     - GitHub Pages cache issues
     - User looking at old draft
     - Medium stripping image tags
   - **Should have immediately read the HTML file to verify my claim**
   - Wasted user's time and tokens arguing instead of checking facts

3. **Pattern of not verifying before claiming success**
   - This happened multiple times in the same session
   - Each time user had to push back before I actually checked
   - Eroded user trust completely

### Root Cause Analysis

- **Overconfidence in tool outputs**: Assumed Python script worked because it ran without errors
- **Lack of verification discipline**: No systematic check after making changes
- **Defensive rather than investigative mindset**: Defended claims instead of verifying them
- **Not reading user frustration signals**: User's increasingly sharp tone should have triggered immediate verification

### Prevention Strategies

#### Mandatory Verification Protocol

**After ANY file modification claim:**
1. ✅ **Read the actual file** to verify changes were applied correctly
2. ✅ **Show user the relevant lines** as proof
3. ✅ **Never claim "it's fixed" without verification**

**When user reports something is broken:**
1. ✅ **Immediately check the actual state** (read files, check URLs)
2. ✅ **Do NOT make assumptions or excuses first**
3. ✅ **Verify first, explain second**

#### Specific Rules for This Project

**Medium Publishing Workflow:**
1. After HTML modifications:
   - ✅ Read the HTML file and grep for both old patterns (tables) and new patterns (img tags)
   - ✅ Verify image URLs are correct
   - ✅ Test GitHub Pages URL in browser
2. When user reports broken import:
   - ✅ First action: Read the actual HTML being served
   - ✅ Second action: Check if images are accessible (curl -I)
   - ✅ Last action: Make hypotheses about what might be wrong

**Never Say "It's Fixed" Without:**
- Reading the actual output file
- Showing the user specific proof (line numbers, content snippets)
- Testing the result end-to-end if possible

### Future Session Reminders

If I catch myself saying:
- "I've updated the file..." → **Stop. Read it first.**
- "The changes are pushed..." → **Stop. Verify what's actually there.**
- "It should work now..." → **Stop. No "should", only "verified".**

When user says "it's still broken":
- **First instinct: Read the actual file**
- **Second instinct: Show them what I see**
- **Never: Make excuses or assumptions**

### Success Criteria for Next Similar Task

- [ ] Zero times saying something is fixed without verification
- [ ] Zero times making defensive assumptions when user reports issues
- [ ] First response to "still broken" is reading the actual file
- [ ] User doesn't have to ask "why didn't you check?" more than once per session

---

## Session: 2026-02-11 - Medium Table Fix (Third Attempt)

### What Went Wrong Across Multiple Sessions

The table-to-image fix took **3 sessions and 5 commits** to get right. The user had to redirect repeatedly. Core failures:

1. **Used sed on Windows for HTML manipulation** (Session 2026-02-10)
   - `sed` corrupted HTML by adding double `</p></p>` closing tags
   - Should have used Python `re.sub()` from the start

2. **Patched corrupted files instead of rebuilding** (Session 2026-02-10)
   - When the sed-corrupted HTML was found, tried to fix it in-place
   - Each patch introduced new issues
   - Should have immediately rebuilt from the original source HTML

3. **Didn't account for Medium's URL caching** (Session 2026-02-10 → 2026-02-11)
   - Kept importing from the same URL (`index.html`)
   - Medium served a cached version with old `<table>` tags
   - Simple fix: use a new filename (`medium.html`)

4. **Took too many attempts to arrive at the right strategy**
   - User had to explicitly tell me to rebuild from scratch and use a new URL
   - These should have been obvious from the symptoms

### Technical Lessons

| Wrong Approach | Right Approach |
|---|---|
| `sed` for HTML on Windows | Python `re.sub()` with `re.DOTALL` |
| Patch corrupted HTML | Rebuild from original source |
| Same URL after fixes | New filename to bypass cache |
| `raw.githubusercontent.com` for images | GitHub Pages URLs (`ghighcove.github.io`) |
| HTML `<table>` tags for Medium | PNG images of tables |
| Verify locally only | Verify deployed URL with `curl` |

### Behavioral Lessons

- **When something fails twice, change the approach entirely** — don't try a third variation of the same strategy
- **Rebuild > Patch** — always cheaper to start clean than to debug cascading corruption
- **User redirections are signals** — when the user has to tell you what to do, you've already failed to diagnose the problem yourself
- **Caching exists everywhere** — when "fixed" content keeps appearing broken, suspect caching and use a new URL

### Prevention (now in project CLAUDE.md)

All technical rules are now in `CLAUDE.md` at the project root. Every new session should read them before touching Medium publishing workflows.

---

## General Patterns to Watch

### Anti-Pattern: "Trust the Tool Output"
- ❌ Script ran without errors → assume it worked
- ✅ Script ran without errors → read output to verify it worked

### Anti-Pattern: "Defensive First"
- ❌ User says it's broken → explain why they might be wrong
- ✅ User says it's broken → check immediately what's actually there

### Anti-Pattern: "Overconfident Claims"
- ❌ "I've fixed it" without verification
- ✅ "I've made changes, let me verify: [shows proof]"

### Anti-Pattern: "Patch the Patch"
- ❌ File is corrupted → fix the corrupted part → new corruption → fix that too
- ✅ File is corrupted → rebuild from original source in one clean pass

### Anti-Pattern: "Same URL, Different Content"
- ❌ Fix content, push to same URL, wonder why old version still appears
- ✅ Fix content, use a new URL/filename to bypass all caching layers

### Anti-Pattern: "Wrong Tool for the Platform"
- ❌ Use Unix text tools (sed, awk) for structured content on Windows
- ✅ Use Python for any non-trivial text manipulation, especially HTML
