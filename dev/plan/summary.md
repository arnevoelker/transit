# Transit Automation - Executive Summary

## The Problem

Currently, processing a single meeting transcript requires:
- **5 manual commands**
- **~10 minutes of human time**
- **Context switching between tools**
- **Potential for human error** (wrong speaker names, missed steps, incorrect filing)

## The Solution

An intelligent, automated pipeline that:
- **Monitors** the input folder automatically
- **Detects** project type from filename (WIR24 vs general)
- **Identifies** speakers using filename patterns + audio profiles
- **Processes** with project-specific enhancements
- **Files** to the correct location
- **Notifies** when complete

## Key Innovation: Audio Profile Library

When speakers are identified (manually or automatically), the system:
1. Extracts a 3-5 second audio snippet from their first clear speech
2. Stores it in a voice profile library
3. Uses these profiles to identify speakers in future recordings
4. Continuously improves with each processed file

This creates a learning system that gets better over time.

## Implementation in 3 Phases

### Phase 1: Core Automation (Week 1)
**Reduce 5 commands → 1 command**
- Chain all existing tools together
- Add filename-based speaker detection
- Auto-enhance WIR24 files
- Auto-file to correct locations

### Phase 2: Background Service (Week 2)
**Reduce 1 command → 0 commands**
- File watcher monitors input folder
- Automatic processing on file arrival
- Desktop notifications on success
- Email alerts on failure

### Phase 3: Audio Profiles (Week 3)
**Build foundation for voice recognition**
- Extract speaker audio samples
- Build voice profile library
- Prepare for future voice-based matching

## Benefits

**Time Savings:**
- 95% reduction in manual work (10 min → 30 sec)
- Eliminates context switching
- Processes files while you work on other things

**Quality Improvements:**
- Consistent speaker naming
- Automatic terminology corrections
- No manual filing errors
- Audio profile library for future improvements

**Scalability:**
- Handle multiple files in batch
- Easy to add new projects
- Learning system improves over time

## Timeline & Effort

- **Week 1:** Phase 1 (6-8 hours)
- **Week 2:** Phase 2 (3-4 hours)
- **Week 3:** Phase 3 (4-5 hours)
- **Total:** 13-17 hours of development

## Technical Highlights

- Python watchdog for file monitoring
- macOS launchd for background service
- FFmpeg for audio extraction
- AssemblyAI for transcription (existing)
- Email + desktop notifications
- JSON database for speaker profiles

## Future Possibilities (Phase 4+)

- Voice-based speaker identification (95%+ accuracy)
- Support for additional projects beyond WIR24
- Web dashboard for monitoring
- Slack/Teams integration
- Automatic action item extraction
- Calendar integration

## Next Steps

1. Review detailed documentation in this folder
2. Approve overall approach
3. Begin Phase 1 development
4. Test with sample files
5. Deploy incrementally (Phase 1 → 2 → 3)
