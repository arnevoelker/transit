# Fix Plan: Batch Processing Pipeline Bugs

## Executive Summary

Two critical bugs prevent proper batch processing in workbench mode:

1. **Bug #1:** Case-insensitive file detection - Files with uppercase extensions (`.WAV`) are not detected
2. **Bug #2:** Source audio files not moved - After transcription, the original audio file remains in the input folder

Both bugs must be fixed together for the pipeline to work correctly.

---

## Bug #1: Case-Insensitive Audio File Detection

### Problem Statement

The file `merged_output.WAV` (with uppercase extension) is detected by the video preprocessor as "ready for transcription" but never gets transcribed by the batch processor.

**Observed behavior:**
```
🎬 Running video preprocessor...
   Found 1 media files in directory
   Checking: merged_output.WAV
      Looking for JSON at: /Users/av/0-prod/transit/workbench/output/merged_output/merged_output.json

✅ merged_output.WAV (345.5MB) - Ready for transcription

✨ No unprocessed audio files found
All files appear to be already processed
```

### Root Cause Analysis

### Issue Location
**File:** `src/transit/batch_process.py`
**Lines:** 586-593

### The Bug
The batch processor only searches for **lowercase** audio file extensions:

```python
for ext in ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']:
    pattern = os.path.join(INPUT_DIR if os.path.exists(INPUT_DIR) else ".", f"*{ext}")
    for audio_file in glob.glob(pattern):
        # ... process file
```

This means:
- ✅ Files like `audio.wav` are detected
- ❌ Files like `audio.WAV` are **NOT** detected

### Why Video Preprocessor Works Correctly
**File:** `src/transit/video_preprocessor.py`
**Lines:** 89-92

The video preprocessor searches for **both cases**:

```python
for ext in all_extensions:
    media_files.extend(glob.glob(f"*{ext}"))        # lowercase
    media_files.extend(glob.glob(f"*{ext.upper()}")) # uppercase ← This is the key difference!
```

This inconsistency between the two modules causes the bug.

## Solution

### Option 1: Match Video Preprocessor Pattern (Recommended)
Update `batch_process.py` to search both lowercase and uppercase extensions, exactly like the video preprocessor does.

**Change in lines 586-593:**

```python
# Current (buggy):
for ext in ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']:
    pattern = os.path.join(INPUT_DIR if os.path.exists(INPUT_DIR) else ".", f"*{ext}")
    for audio_file in glob.glob(pattern):
        # ...

# Fixed:
for ext in ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']:
    pattern = os.path.join(INPUT_DIR if os.path.exists(INPUT_DIR) else ".", f"*{ext}")
    for audio_file in glob.glob(pattern):
        # ... process file
    # Also search uppercase
    pattern_upper = os.path.join(INPUT_DIR if os.path.exists(INPUT_DIR) else ".", f"*{ext.upper()}")
    for audio_file in glob.glob(pattern_upper):
        # ... process file (same logic)
```

### Option 2: Case-Insensitive Glob (Alternative)
Use case-insensitive pattern matching if the file system supports it.

```python
# On case-insensitive file systems (macOS default):
pattern = os.path.join(INPUT_DIR, f"*{ext}")
# This would match both .wav and .WAV automatically
```

**However:** This is filesystem-dependent and not portable. Option 1 is safer.

## Implementation Steps

1. **Locate the bug:** `src/transit/batch_process.py` lines 586-593
2. **Add uppercase search:** Add a second `glob.glob()` call with `ext.upper()` for each extension
3. **Refactor for clarity:** Consider extracting the search logic to avoid duplication
4. **Test with the current file:** Run batch processor on `merged_output.WAV`
5. **Verify both cases work:** Test with both `test.wav` and `test.WAV` files

## Testing Plan

### Test Case 1: Uppercase Extension
```bash
# Current file should now be detected
python src/transit/batch_process.py
# Expected: merged_output.WAV should be queued for transcription
```

### Test Case 2: Mixed Case Files
Create test files with different cases:
```bash
cd workbench/input
touch test1.wav test2.WAV test3.Mp3 test4.MP3
```

Expected result: All files should be detected regardless of extension case.

## Additional Notes

### Why This Bug Existed
- The codebase evolved with two different modules handling file discovery
- Video preprocessor was written with case-awareness (likely because video files often come from cameras with uppercase extensions)
- Batch processor was written assuming lowercase extensions (common convention)
- No consistency check between the two modules

### Prevention
Consider creating a shared utility function for file discovery:

```python
def find_media_files(directory, extensions, case_insensitive=True):
    """
    Find media files with optional case-insensitive matching

    Args:
        directory: Directory to search
        extensions: List of extensions (e.g., ['.mp3', '.wav'])
        case_insensitive: Search both cases (default True)

    Returns:
        List of file paths
    """
    files = []
    for ext in extensions:
        pattern = os.path.join(directory, f"*{ext}")
        files.extend(glob.glob(pattern))
        if case_insensitive:
            pattern_upper = os.path.join(directory, f"*{ext.upper()}")
            files.extend(glob.glob(pattern_upper))
    return files
```

This could be used by both modules to ensure consistency.

## Impact Assessment

- **Severity:** Medium - Files with uppercase extensions are silently ignored
- **Frequency:** Low - Most audio files use lowercase extensions by convention
- **Workaround:** Rename file to lowercase extension (`mv merged_output.WAV merged_output.wav`)
- **Fix Complexity:** Low - Single location, straightforward change

## Related Files to Review

After fixing, review these files for similar issues:
1. `src/transit/video_preprocessor.py` - Already correct
2. `src/transit/organize_files.py` - Check if it has similar pattern matching
3. `src/transit/label_speakers.py` - Check file discovery logic

### Success Criteria for Bug #1

✅ `merged_output.WAV` is detected and queued for transcription
✅ Both uppercase and lowercase extensions work consistently
✅ Video preprocessor and batch processor behavior is aligned

---

## Bug #2: Source Audio Files Not Moved to Output

### Problem Statement

After successful transcription, the output files (JSON, SRT, MD) are correctly moved to the output folder, but the **source audio file** remains in the input folder.

**Observed behavior:**
```
Input folder still contains:
- 20251007-djitest.wav  ← Should have been moved!

Output folder contains:
- 20251007-djitest.json
- 20251007-djitest new_transcript_aai.json
- 20251007-djitest subtitle_aai.srt
- 20251007-djitest screenplay_aai.md
```

### Root Cause Analysis

**File:** `src/transit/batch_process.py`
**Function:** `organize_files_for_audio()`
**Lines:** 278-285

The `organize_files_for_audio()` function searches for files to move using these patterns:

```python
patterns = [
    f"{base_name}.mp3",                      # ❌ Only .mp3
    f"{base_name}.mp4",                      # ❌ Only .mp4
    f"{base_name}.json",                     # ✅ Transcript
    f"{base_name} new_transcript_aai.json",  # ✅ Processed transcript
    f"{base_name} subtitle_aai.srt",         # ✅ Subtitles
    f"{base_name} screenplay_aai.md"         # ✅ Screenplay
]
```

**The bug:** The patterns list is **missing most audio extensions**:
- Missing: `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`
- Present: Only `.mp3` and `.mp4`

When a `.wav` file is processed, it's not in the patterns list, so it doesn't get moved to the output folder.

### Solution for Bug #2

Update the patterns list to include all supported audio extensions (both lowercase and uppercase for consistency with Bug #1 fix).

**Change in lines 278-285:**

```python
# Current (buggy):
patterns = [
    f"{base_name}.mp3",
    f"{base_name}.mp4",
    f"{base_name}.json",
    f"{base_name} new_transcript_aai.json",
    f"{base_name} subtitle_aai.srt",
    f"{base_name} screenplay_aai.md"
]

# Fixed:
patterns = [
    # Audio files (all supported formats)
    f"{base_name}.mp3",
    f"{base_name}.MP3",
    f"{base_name}.wav",
    f"{base_name}.WAV",
    f"{base_name}.m4a",
    f"{base_name}.M4A",
    f"{base_name}.aac",
    f"{base_name}.AAC",
    f"{base_name}.flac",
    f"{base_name}.FLAC",
    f"{base_name}.ogg",
    f"{base_name}.OGG",
    # Video files
    f"{base_name}.mp4",
    f"{base_name}.MP4",
    # Transcript outputs
    f"{base_name}.json",
    f"{base_name} new_transcript_aai.json",
    f"{base_name} subtitle_aai.srt",
    f"{base_name} screenplay_aai.md"
]
```

**Alternative (cleaner):** Use a programmatic approach:

```python
# Define supported extensions
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
VIDEO_EXTENSIONS = ['.mp4']

# Build patterns dynamically
patterns = []

# Add audio/video files (both cases)
for ext in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
    patterns.append(f"{base_name}{ext}")
    patterns.append(f"{base_name}{ext.upper()}")

# Add transcript outputs
patterns.extend([
    f"{base_name}.json",
    f"{base_name} new_transcript_aai.json",
    f"{base_name} subtitle_aai.srt",
    f"{base_name} screenplay_aai.md"
])
```

### Why This Bug Existed

The `organize_files_for_audio()` function was originally designed for MP3 files only (hence the function name in the original code). As support for additional audio formats was added to the transcription pipeline, the patterns list was never updated.

### Testing Plan for Bug #2

1. Process a `.wav` file
2. Verify the source `.wav` file is moved to output folder
3. Test with other extensions (`.m4a`, `.aac`, etc.)
4. Verify both uppercase and lowercase extensions work

### Success Criteria for Bug #2

✅ Source audio files are moved to output folder after transcription
✅ All supported audio formats are handled (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`)
✅ Both uppercase and lowercase extensions work
✅ Input folder is empty after successful processing

---

## Combined Implementation Plan

### Step 1: Fix Bug #1 (Case-Insensitive Detection)
- Location: `src/transit/batch_process.py` lines 586-593
- Action: Add uppercase extension search in batch processor

### Step 2: Fix Bug #2 (Missing Audio Extensions)
- Location: `src/transit/batch_process.py` lines 278-285
- Action: Add all audio extensions to organize patterns list

### Step 3: Extract Shared Constants (Recommended)
Create a shared constants file or section at the top of the module:

```python
# Supported file extensions
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
```

Use these constants in:
1. File detection loop (lines 586-593)
2. `organize_files_for_audio()` patterns (lines 278-285)
3. Any other file discovery logic

### Step 4: Integration Testing
Test the complete pipeline:

```bash
# 1. Place test files in input folder
cd workbench/input
cp /path/to/test1.wav .
cp /path/to/test2.WAV .
cp /path/to/test3.mp3 .

# 2. Run batch processor
cd /Users/av/0-prod/transit
python src/transit/batch_process.py

# 3. Verify results
# - All files detected and transcribed
# - All source files moved to output folders
# - Input folder is empty
```

### Expected Outcome After Both Fixes

```
workbench/input/
  └── (empty)

workbench/output/
  ├── test1/
  │   ├── test1.wav              ← Source file moved!
  │   ├── test1.json
  │   ├── test1 new_transcript_aai.json
  │   ├── test1 subtitle_aai.srt
  │   └── test1 screenplay_aai.md
  ├── test2/
  │   ├── test2.WAV              ← Uppercase extension handled!
  │   ├── test2.json
  │   ├── test2 new_transcript_aai.json
  │   ├── test2 subtitle_aai.srt
  │   └── test2 screenplay_aai.md
  └── test3/
      ├── test3.mp3
      ├── test3.json
      ├── test3 new_transcript_aai.json
      ├── test3 subtitle_aai.srt
      └── test3 screenplay_aai.md
```

## Overall Success Criteria

✅ Files with any case extension are detected and transcribed
✅ Source audio files are moved to output folder
✅ Input folder is empty after processing
✅ Output folders contain all related files (source + transcripts)
✅ No regression in existing functionality
