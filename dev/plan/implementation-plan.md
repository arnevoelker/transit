# Implementation Plan

## Overview

This document outlines the phased implementation approach for the Transit Automation System.

## Development Timeline

### Week 1: Phase 1 - Core Automation (6-8 hours)

**Goal:** Chain existing tools into single-command workflow

**Key Deliverables:**
- `orchestrator.py` - Main pipeline coordinator
- Enhanced `processor_aai.py` with `--auto-assign` flag
- `speaker_detector.py` with filename pattern matching
- Initial `speakers_db.json`

**Tasks:**
1. Create orchestrator.py (3h)
   - Project type detection
   - Pipeline chaining
   - Error handling
   - Logging

2. Enhance processor_aai.py (2h)
   - Add --auto-assign flag
   - Maintain backward compatibility
   - Prepare for audio extraction

3. Create speaker_detector.py (2h)
   - Filename pattern matching
   - Database lookup
   - Confidence scoring

4. Initialize speakers_db.json (1h)
   - WIR24 patterns
   - Common participants
   - Database utilities

**Success Criteria:**
- Reduce 5 commands → 1 command
- 80%+ speaker auto-detection
- WIR24 files auto-enhanced
- Files auto-organized

---

### Week 2: Phase 2 - Background Service (3-4 hours)

**Goal:** Eliminate manual triggering

**Key Deliverables:**
- `watcher.py` - File monitoring service
- `notification_manager.py` - Notifications
- launchd service configuration
- Installation scripts

**Tasks:**
1. Create watcher.py (2h)
   - Watchdog integration
   - Debouncing logic
   - Queue management
   - Daemon mode

2. Create notification_manager.py (1.5h)
   - macOS desktop notifications
   - Email alerts (SMTP)
   - Templates

3. Configure launchd service (0.5h)
   - Create .plist file
   - Environment variables
   - Installation script

**Success Criteria:**
- Zero manual commands
- File detection < 3 seconds
- Desktop notifications 100%
- Email on all failures

---

### Week 3: Phase 3 - Audio Profile System (4-5 hours)

**Goal:** Build speaker voice profile library

**Key Deliverables:**
- `audio_extractor.py` - Audio snippet extraction
- Enhanced `speakers_db.json` with audio samples
- Initial profile library (40+ samples)
- Integration with pipeline

**Tasks:**
1. Create audio_extractor.py (2h)
   - FFmpeg-based extraction
   - Audio normalization
   - Database updates

2. Enhance speakers_db.json (1h)
   - Add audio profile schema
   - Migration if needed

3. Build initial library (1h)
   - Process existing transcripts
   - Extract profiles
   - Validate quality

4. Integrate with pipeline (1h)
   - Auto-extract during processing
   - Error handling

**Success Criteria:**
- Audio profiles extracted automatically
- Library contains 40+ samples
- Quality score > 0.85 average
- No manual intervention

---

## Detailed Task Breakdown

### Phase 1 Tasks

#### Task 1.1: orchestrator.py
```python
# Core functions:
def detect_project_type(filename: str) -> str
def process_wir24_pipeline(file_path: str) -> bool
def process_general_pipeline(file_path: str) -> bool
def handle_error(error: Exception) -> None
```

#### Task 1.2: processor_aai.py
```python
# New flags:
--auto-assign "A:Arne,B:Rebecca"
--extract-profiles  # Phase 3 prep
```

#### Task 1.3: speaker_detector.py
```python
# Core functions:
def analyze_filename(filename: str) -> dict
def lookup_speakers(project: str) -> list
def calculate_confidence(signals: dict) -> float
```

### Phase 2 Tasks

#### Task 2.1: watcher.py
```python
# Watchdog event handler
class TransitFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Queue file for processing
```

#### Task 2.2: notification_manager.py
```python
def send_desktop_notification(title, message, file_path)
def send_email_alert(subject, body, to_address)
```

### Phase 3 Tasks

#### Task 3.1: audio_extractor.py
```python
def extract_speaker_sample(json_path, speaker, audio_file) -> str
def normalize_audio(input_file, output_file) -> None
def add_audio_profile(speaker, audio_file, metadata) -> None
```

---

## Testing Strategy

### Unit Tests
- Each component independently
- Mock external dependencies
- pytest framework

### Integration Tests
- End-to-end pipeline
- Real file processing
- Notification delivery

### Manual Testing
- Real WIR24 meetings
- Speaker detection accuracy
- Error scenarios

---

## Deployment Checklist

### Phase 1
- [ ] Deploy orchestrator.py
- [ ] Update processor_aai.py
- [ ] Create speakers_db.json
- [ ] Test with sample files

### Phase 2
- [ ] Deploy watcher.py
- [ ] Install launchd service
- [ ] Configure notifications
- [ ] Monitor for 48 hours

### Phase 3
- [ ] Deploy audio_extractor.py
- [ ] Build profile library
- [ ] Test integration

---

## Timeline Summary

- **Week 1:** Core automation (single command)
- **Week 2:** Background service (zero commands)
- **Week 3:** Audio profiles (learning system)
- **Total:** 13-17 hours development

## Next Steps

1. Review and approve plan
2. Begin Phase 1 development
3. Test incrementally
4. Deploy phase by phase
