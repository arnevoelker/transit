# Transit Automation Project - Development Plan

**Project:** Intelligent Transcript Processing Pipeline with Audio-Based Speaker Recognition  
**Created:** 2024-11-04  
**Status:** Planning Phase

## Overview

This directory contains the complete planning documentation for automating the transcript processing workflow. The goal is to reduce manual intervention from 5 commands to zero commands while maintaining quality and adding intelligent speaker recognition.

## Documentation Structure

- **README.md** (this file) - Project overview and navigation
- **architecture.md** - System architecture, components, and data flow
- **implementation-plan.md** - Phased implementation roadmap with estimates
- **speaker-detection.md** - Speaker detection algorithm and audio profile system
- **configuration.md** - Configuration files, settings, and deployment

## Current Workflow (Manual - 5 Steps)

1. Media file lands in `/Users/av/0-prod/transit/workbench/input`
2. Run `python src/transit/batch_process.py` → extracts audio, transcribes
3. Run `python src/transit/processor_aai.py [json_path]` → manual speaker naming
4. Run `/wir24-transcript [screenplay_path]` → apply corrections, create summary
5. Move folder to `/Users/av/PARA/01 PROJECTS/WIR24 Bank WIR Support 2024/Sessions/`

**Time investment:** ~10 minutes per file, manual context switching, potential for errors

## Target Workflow (Automated - 0 Steps)

1. Media file lands in input folder
2. **System automatically:** detects project type, processes, names speakers, enhances, files
3. Desktop notification when complete

**Time investment:** ~30 seconds to review notification

## Key Features

### Audio-Based Speaker Recognition with Profile Library
- Stores 3-5 second audio snippets from confirmed speaker identifications
- Builds voice profile library over time
- Enables future voice-based matching (Phase 4)
- Uses filename patterns + database for 80%+ confidence auto-assignment

### Intelligent Project Detection
- Analyzes filename patterns (e.g., "WIR24") to route to appropriate pipeline
- WIR24 files get special enhancement treatment
- General files processed without enhancement

### Background Processing
- File watcher service monitors input folder with Python watchdog
- Automatically triggers on new files
- Runs as macOS launchd daemon
- Queue management for multiple files

### Smart Notifications
- **Success:** macOS desktop notification (click to open)
- **Failure:** Email to arne.voelker@aebivoelkerund.com

## Implementation Phases

### Phase 1: Core Automation (6-8 hours)
- orchestrator.py chains existing tools
- Filename-based speaker detection
- Manual trigger (one command)
- 80% reduction in manual work

### Phase 2: Background Service (3-4 hours)
- Watchdog file monitoring
- Desktop + email notifications
- launchd daemon service
- Zero manual commands

### Phase 3: Audio Profile System (4-5 hours)
- Extract audio snippets from speakers
- Build voice profile library
- Foundation for voice recognition

### Phase 4: Voice Recognition (Future)
- Compare speaker embeddings
- Voice-based auto-detection
- 95%+ accuracy target

## Success Metrics

| Metric | Current | Phase 2 | Phase 3+ |
|--------|---------|---------|----------|
| Manual commands | 5 | 0 | 0 |
| Human time per file | ~10 min | ~30 sec | ~30 sec |
| Speaker ID accuracy | 100% | 85% | 95%+ |
| Time savings | - | 95% | 95%+ |

## Getting Started

1. Review **architecture.md** for system design
2. Read **implementation-plan.md** for development roadmap
3. Check **speaker-detection.md** for algorithm details
4. See **configuration.md** for setup requirements

## Contact

Arne Völker (arne.voelker@aebivoelkerund.com)
