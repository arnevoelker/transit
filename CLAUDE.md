# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Transit is an automated transcription and speaker labeling pipeline for audio and video files using AssemblyAI. It processes media files in batch, performs speaker diarization, and outputs multiple formats including JSON, SRT subtitles, and a natural screenplay format.

## Development Setup

### Prerequisites
- Python 3.x
- FFmpeg (optional, for video processing)
- AssemblyAI API key set as `ASSEMBLYAI_API_KEY` environment variable

### Installation
```bash
pip install -r requirements.txt
```

## Key Commands

### Running the Main Pipeline
```bash
# Process all media files in workbench/input/
python -m src.transit.batch_process

# Process specific video file (extracts audio first)
python -m src.transit.video_preprocessor path/to/video.mp4

# Relabel speakers interactively
python -m src.transit.label_speakers path/to/transcript.json

# Generate screenplay format
python -m src.transit.navigation_screenplay path/to/transcript.json

# Organize output files into named folders
python -m src.transit.organize_files
```

## Architecture

### Core Components

1. **batch_process.py** - Main entry point that orchestrates the entire pipeline:
   - Detects unprocessed files in `workbench/input/`
   - Extracts audio from video files
   - Submits to AssemblyAI for transcription
   - Polls for completion
   - Downloads and processes results
   - Generates multiple output formats

2. **video_preprocessor.py** - Handles video-to-audio conversion:
   - Uses FFmpeg to extract high-quality audio
   - Supports wide range of video formats
   - Outputs to `_audio.mp3` files

3. **transcribe_pipeline.py** - Core transcription logic:
   - Manages AssemblyAI API interactions
   - Handles speaker diarization
   - Creates transcript objects
   - Generates output formats

4. **label_speakers.py** - Interactive speaker relabeling:
   - Loads existing transcripts
   - Presents speaker segments for review
   - Allows custom speaker names
   - Preserves original data while updating labels

### Data Flow

```
workbench/input/ → video_preprocessor → AssemblyAI API → JSON transcript
                                                        ↓
                                    SRT, Markdown, Named folders ← output processors
```

### File Naming Convention

- Input: Any audio/video file
- Audio extraction: `<name>_audio.mp3`
- Transcript JSON: `<name> transcript_aai.json`
- SRT subtitles: `<name> screenplay_aai.srt`
- Markdown: `<name> screenplay_aai.md`
- Output folder: `<name>/` containing all related files

## Key Patterns and Conventions

1. **Lazy Processing**: Files are only processed if output doesn't already exist
2. **Monologue Breaking**: Long speaker turns are split at ~45 seconds for readability
3. **Natural Formatting**: Screenplay format uses "SPEAKER:" style with timestamps
4. **Error Handling**: Non-blocking - continues processing other files on errors
5. **File Organization**: Each media file gets its own output directory

## Working with the Code

### Adding New Features
- New output formats: Add to `transcribe_pipeline.py` in the format generation section
- New processors: Create standalone scripts following the pattern of existing ones
- API modifications: Update both `batch_process.py` and `transcribe_pipeline.py`

### Common Modifications

**Changing Output Formats**:
Look in `src/transit/transcribe_pipeline.py` for the format generation functions:
- `generate_srt()` - SRT subtitle format
- `create_natural_screenplay()` - Markdown screenplay format

**Adjusting Speaker Diarization**:
Check `batch_process.py` for the `speaker_boost=True` parameter in the transcription config.

**Modifying File Detection**:
Update the `has_been_processed()` function in `batch_process.py` to change what files are considered "already processed".

## Git Workflow

### Branching Strategy

This project uses a simple two-branch workflow:

- **main** - Production-ready, stable code. Always deployable.
- **develop** - Integration branch for development work. Create feature branches from here.

### Development Process

1. **For new features**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   # Make changes, commit
   git push -u origin feature/your-feature-name
   # Create PR to merge into develop
   ```

2. **For bug fixes**:
   ```bash
   git checkout develop
   git checkout -b bugfix/issue-description
   # Fix bug, commit
   git push -u origin bugfix/issue-description
   # Create PR to merge into develop
   ```

3. **Releasing to production**:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

### Important Notes

- Always work in feature/bugfix branches, never directly on `main` or `develop`
- Keep `main` stable - only merge tested code from `develop`
- Delete feature branches after merging
- Use descriptive branch names (e.g., `feature/add-whisper-support`, `bugfix/fix-uppercase-extension`)

## Important Notes

- No formal test suite exists - test changes manually with sample files
- The project uses direct script execution rather than a package structure
- All scripts are designed to be run from the project root
- The `workbench/` directory is the primary workspace for processing
- API responses are cached as JSON files for debugging and reprocessing