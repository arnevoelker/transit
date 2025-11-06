# System Architecture

## Overview

The Transit Automation System is a multi-component pipeline that monitors, processes, and organizes audio/video transcripts with intelligent speaker identification and project-specific enhancements.

## High-Level Architecture

```
Input Folder (Monitored)
        ↓
    File Watcher (watchdog)
        ↓
    Orchestrator (main coordinator)
        ↓
   ┌────┴────┐
   ↓         ↓
WIR24      General
Pipeline   Pipeline
   ↓         ↓
   └────┬────┘
        ↓
    Components:
    - Audio Processing (batch_process.py)
    - Speaker Detection (speaker_detector.py)
    - Speaker Naming (processor_aai.py)
    - Audio Profile Extraction (audio_extractor.py)
    - WIR24 Enhancement (wir24_enhancer.py)
    - File Organization (file_organizer.py)
    - Notifications (notification_manager.py)
```

## Component Details

### 1. File Watcher
- **Technology:** Python watchdog
- **Purpose:** Monitor input folder for new media files
- **Features:**
  - Debouncing (wait for file copy completion)
  - Queue management
  - Runs as launchd daemon

### 2. Orchestrator
- **Purpose:** Main pipeline coordinator
- **Responsibilities:**
  - Project type detection
  - Component orchestration
  - Error handling
  - Logging

### 3. Speaker Detector
- **Methods:**
  - Filename pattern matching
  - Database lookup
  - Audio profile comparison (Phase 3+)
- **Confidence threshold:** 80%

### 4. Audio Extractor (NEW - Phase 3)
- **Purpose:** Build speaker voice profile library
- **Process:**
  1. Extract 3-5 second audio snippet per speaker
  2. Normalize audio (16kHz mono, MP3)
  3. Store in audio_profiles/
  4. Update speakers_db.json

### 5. WIR24 Enhancer
- **Purpose:** Apply project-specific corrections
- **Features:**
  - Terminology corrections
  - Enhanced screenplay
  - Topic-organized summary

## Data Flow

1. **File arrives** in input folder
2. **Watcher detects** within 3 seconds
3. **Orchestrator analyzes** filename for project type
4. **Audio extracted** from video (if needed)
5. **Transcription** via AssemblyAI
6. **Speaker detection** analyzes filename + database
7. **Auto-assign** if confidence ≥ 80%, else interactive
8. **Audio profiles extracted** and stored
9. **Enhancement applied** (WIR24 only)
10. **Files organized** to destination
11. **Notification sent** (desktop or email)

## Database Structure

### speakers_db.json
```json
{
  "projects": {
    "wir24": {
      "common_participants": ["Arne", "Rebecca", ...],
      "speaker_profiles": {
        "Arne": {
          "audio_samples": [
            {
              "file": "audio_profiles/arne_001.mp3",
              "source": "20251104 WIR24...",
              "confidence": 1.0
            }
          ]
        }
      },
      "filename_patterns": {
        "rebecca.*arne": {
          "speakers": ["Rebecca", "Arne"],
          "confidence": 0.85
        }
      }
    }
  }
}
```

## Deployment

- **Service:** macOS launchd daemon
- **Monitoring:** Log files + health checks
- **Notifications:** Desktop (success) + Email (failure)

For detailed component specifications, see full architecture document.
