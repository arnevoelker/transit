import assemblyai as aai
import json
import os
import glob
import time
import shutil
from pathlib import Path
import copy
import textwrap
import subprocess
import sys

# Workbench configuration
WORKBENCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'workbench')
INPUT_DIR = os.path.join(WORKBENCH_DIR, 'input')
OUTPUT_DIR = os.path.join(WORKBENCH_DIR, 'output')

def seconds_to_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def milliseconds_to_hms(milliseconds):
    """Convert milliseconds to HH:MM:SS format"""
    seconds = milliseconds / 1000
    return seconds_to_hms(seconds)

def milliseconds_to_srt_time(milliseconds):
    """Convert milliseconds to SRT timestamp format (HH:MM:SS,mmm)"""
    total_seconds = milliseconds / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    ms = int(milliseconds % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

def group_words_into_segments(words, max_gap_ms=2000, max_words_per_segment=15):
    """Group words into segments based on time gaps and word count"""
    if not words:
        return []
    
    segments = []
    current_segment = {
        'words': [words[0]],
        'speaker': words[0]['speaker'],
        'start': words[0]['start'], 
        'end': words[0]['end']
    }
    
    for word in words[1:]:
        time_gap = word['start'] - current_segment['end']
        speaker_changed = word['speaker'] != current_segment['speaker']
        segment_too_long = len(current_segment['words']) >= max_words_per_segment
        
        if speaker_changed or time_gap > max_gap_ms or segment_too_long:
            # Finalize current segment
            current_segment['text'] = ' '.join([w['text'] for w in current_segment['words']])
            segments.append(current_segment)
            
            # Start new segment
            current_segment = {
                'words': [word],
                'speaker': word['speaker'],
                'start': word['start'],
                'end': word['end']
            }
        else:
            # Add word to current segment
            current_segment['words'].append(word)
            current_segment['end'] = word['end']
    
    # Add final segment
    if current_segment['words']:
        current_segment['text'] = ' '.join([w['text'] for w in current_segment['words']])
        segments.append(current_segment)
    
    return segments

def write_srt(words, file_name):
    """Write SRT file from AssemblyAI words data"""
    segments = group_words_into_segments(words)
    
    counter = 1
    with open(file_name, 'w') as file:
        for segment in segments:
            start_time = milliseconds_to_srt_time(segment['start'])
            end_time = milliseconds_to_srt_time(segment['end'])
            speaker = segment['speaker'].strip()
            text = segment['text']
            
            file.write(f"{counter}\n")
            file.write(f"{start_time} --> {end_time}\n")
            file.write(f"[{speaker.upper()}]\n")
            for line in textwrap.wrap(text, 65):
                file.write(f"{line}\n")
            file.write("\n")
            counter += 1

def is_sentence_boundary(text):
    """Check if text ends with sentence boundary punctuation"""
    return text.strip().endswith(('.', '!', '?'))

def write_md(words, file_name):
    """Write natural speaker-turn Markdown file from AssemblyAI words data"""
    if not words:
        return
    
    with open(file_name, 'w') as file:
        current_speaker = words[0]['speaker']
        current_words = []
        current_start = words[0]['start']
        
        for word in words:
            # Check if speaker changed
            if word['speaker'] != current_speaker:
                # Write current speaker's turn
                if current_words:
                    speaker = current_speaker.strip()
                    timecode = milliseconds_to_hms(current_start)
                    text = ' '.join(current_words)
                    file.write(f"{speaker.upper()} ({timecode}):\n{text}\n\n")
                
                # Start new speaker turn
                current_speaker = word['speaker']
                current_words = [word['text']]
                current_start = word['start']
            else:
                # Same speaker - check if we need to break long monologue
                current_words.append(word['text'])
                
                # Check if current monologue exceeds 45 seconds
                current_duration = (word['end'] - current_start) / 1000  # Convert to seconds
                if current_duration > 45:
                    # Look for sentence boundary to break
                    current_text = ' '.join(current_words)
                    if is_sentence_boundary(current_text):
                        # Write current segment
                        speaker = current_speaker.strip()
                        timecode = milliseconds_to_hms(current_start)
                        file.write(f"{speaker.upper()} ({timecode}):\n{current_text}\n\n")
                        
                        # Start new segment for same speaker
                        current_words = []
                        current_start = word['end']  # Start from end of last word
        
        # Write final speaker turn
        if current_words:
            speaker = current_speaker.strip()
            timecode = milliseconds_to_hms(current_start)
            text = ' '.join(current_words)
            file.write(f"{speaker.upper()} ({timecode}):\n{text}\n\n")

def group_words_into_navigation_segments(words, segment_duration_ms=45000):
    """
    Group words into fixed-duration segments for navigation purposes
    
    Args:
        words: List of word objects with start, end, text, speaker
        segment_duration_ms: Duration of each segment in milliseconds (default: 45 seconds)
    
    Returns:
        List of segments with consistent duration for easy navigation
    """
    if not words:
        return []
    
    segments = []
    
    # Get the total duration
    start_time = words[0]['start']
    end_time = words[-1]['end']
    total_duration = end_time - start_time
    
    # Create segments at fixed intervals
    current_time = start_time
    
    while current_time < end_time:
        segment_end = min(current_time + segment_duration_ms, end_time)
        
        # Find words in this time range
        segment_words = []
        for word in words:
            if word['start'] >= current_time and word['start'] < segment_end:
                segment_words.append(word)
        
        if segment_words:
            # Build segment text with speaker changes indicated
            segment_text_parts = []
            current_speaker = None
            current_speaker_text = []
            
            for word in segment_words:
                if word['speaker'] != current_speaker:
                    # Speaker changed, save previous speaker's text
                    if current_speaker is not None and current_speaker_text:
                        speaker_line = f"{current_speaker.upper()}: {' '.join(current_speaker_text)}"
                        segment_text_parts.append(speaker_line)
                    
                    # Start new speaker
                    current_speaker = word['speaker']
                    current_speaker_text = [word['text']]
                else:
                    current_speaker_text.append(word['text'])
            
            # Add final speaker's text
            if current_speaker is not None and current_speaker_text:
                speaker_line = f"{current_speaker.upper()}: {' '.join(current_speaker_text)}"
                segment_text_parts.append(speaker_line)
            
            segment = {
                'start': current_time,
                'end': segment_end,
                'duration_seconds': (segment_end - current_time) / 1000,
                'text': '\n\n'.join(segment_text_parts),
                'word_count': len(segment_words),
                'speakers': list(set(word['speaker'] for word in segment_words))
            }
            
            segments.append(segment)
        
        current_time = segment_end
    
    return segments

def write_navigation_screenplay(words, file_name, segment_duration_seconds=45):
    """Write navigation-friendly screenplay with fixed-duration segments"""
    segment_duration_ms = segment_duration_seconds * 1000
    segments = group_words_into_navigation_segments(words, segment_duration_ms)
    
    with open(file_name, 'w') as file:
        file.write(f"# Navigation Screenplay ({segment_duration_seconds}s segments)\n\n")
        file.write(f"Total segments: {len(segments)}\n")
        file.write(f"Total duration: {milliseconds_to_hms(words[-1]['end'] - words[0]['start']) if words else '0:00:00'}\n\n")
        file.write("---\n\n")
        
        for i, segment in enumerate(segments, 1):
            start_time = milliseconds_to_hms(segment['start'])
            end_time = milliseconds_to_hms(segment['end'])
            duration = f"{segment['duration_seconds']:.1f}s"
            speakers = ', '.join(segment['speakers'])
            
            file.write(f"## Segment {i} ({start_time} - {end_time}) [{duration}]\n")
            file.write(f"**Speakers:** {speakers} | **Words:** {segment['word_count']}\n\n")
            file.write(f"{segment['text']}\n\n")
            file.write("---\n\n")

def setup_api_key():
    """Setup AssemblyAI API key from environment or user input"""
    if 'ASSEMBLYAI_API_KEY' not in os.environ:
        api_key = input("Please enter your AssemblyAI API key: ").strip()
        if not api_key:
            raise ValueError("API key is required")
        os.environ['ASSEMBLYAI_API_KEY'] = api_key
        aai.settings.api_key = api_key
    else:
        aai.settings.api_key = os.environ['ASSEMBLYAI_API_KEY']

def get_base_filename(filepath):
    """Get base filename without extension"""
    return Path(filepath).stem

def organize_files_for_audio(audio_file, use_workbench=False):
    """Organize all files related to an audio file into a folder"""
    base_name = get_base_filename(audio_file)
    
    # Determine folder location
    if use_workbench:
        folder_name = os.path.join(OUTPUT_DIR, base_name)
    else:
        folder_name = base_name
    
    # Get directory where files are currently located
    file_dir = os.path.dirname(audio_file) or "."
    
    # Find all related files
    patterns = [
        f"{base_name}.mp3",
        f"{base_name}.mp4", 
        f"{base_name}.json",
        f"{base_name} new_transcript_aai.json",
        f"{base_name} subtitle_aai.srt",
        f"{base_name} screenplay_aai.md"
    ]
    
    related_files = []
    for pattern in patterns:
        file_path = os.path.join(file_dir, pattern)
        if os.path.exists(file_path):
            related_files.append(file_path)
    
    if not related_files:
        print(f"⚠️  No related files found for {audio_file}")
        return False
    
    print(f"📁 Organizing files into folder: {folder_name}")
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
        print(f"   ✅ Created folder: {folder_name}")
    
    # Move all related files
    moved_count = 0
    for file in related_files:
        filename = os.path.basename(file)
        destination = os.path.join(folder_name, filename)
        
        if os.path.exists(destination):
            print(f"   ⚠️  File already exists in folder: {filename}")
        else:
            try:
                shutil.move(file, destination)
                print(f"   📄 Moved: {filename}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {filename}: {e}")
    
    print(f"   ✅ Organized {moved_count} files into {folder_name}/")
    return True

def find_unprocessed_mp3_files(search_dir=None):
    """Find MP3 files that haven't been processed yet"""
    if search_dir is None:
        # Default to workbench input if it exists, otherwise current directory
        if os.path.exists(INPUT_DIR):
            search_dir = INPUT_DIR
        else:
            search_dir = "."
    
    # Search for MP3 files in the specified directory
    search_pattern = os.path.join(search_dir, "*.mp3")
    mp3_files = glob.glob(search_pattern)
    unprocessed = []
    
    for mp3_file in mp3_files:
        base_name = get_base_filename(mp3_file)
        # Check in output directory if using workbench
        if search_dir == INPUT_DIR:
            output_folder = os.path.join(OUTPUT_DIR, base_name)
            json_file = os.path.join(output_folder, f"{base_name}.json")
        else:
            # Original behavior for current directory
            json_file = f"{base_name}.json"
        
        # Check if JSON already exists
        if not os.path.exists(json_file):
            unprocessed.append(mp3_file)
    
    return unprocessed

def transcribe_and_process(audio_file):
    """Complete pipeline: transcribe + process"""
    base_name = get_base_filename(audio_file)
    
    # Detect if we're using workbench mode
    use_workbench = INPUT_DIR in os.path.abspath(audio_file)
    
    # Determine output directory
    if use_workbench:
        # Files are saved directly to input dir first, then organized to output
        output_dir = os.path.dirname(audio_file)
    else:
        output_dir = "."
    
    # Generate filenames with base name prepended
    json_file = os.path.join(output_dir, f"{base_name}.json")  # Main transcript
    processed_json = os.path.join(output_dir, f"{base_name} new_transcript_aai.json")  # Processed version
    srt_file = os.path.join(output_dir, f"{base_name} subtitle_aai.srt")
    md_file = os.path.join(output_dir, f"{base_name} screenplay_aai.md")
    
    print(f"\n{'='*60}")
    print(f"Processing: {audio_file}")
    print(f"{'='*60}")
    
    # Step 1: Transcribe
    print("🎯 Starting transcription...")
    start_time = time.time()
    
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        format_text=True,
        punctuate=True,
        speech_model=aai.SpeechModel.best,
        language_detection=True,
    )
    
    try:
        transcript = transcriber.transcribe(audio_file, config=config)
        
        # Check for errors more robustly
        error_msg = getattr(transcript, 'error', None)
        if error_msg:
            print(f"❌ Transcription error: {error_msg}")
            return False
        
        # Also check status if available
        status = getattr(transcript, 'status', None)
        if status and status.lower() in ['error', 'failed']:
            print(f"❌ Transcription failed with status: {status}")
            return False
            
        # Build transcript data - use getattr for optional attributes
        transcript_data = {
            'id': getattr(transcript, 'id', 'unknown'),
            'text': getattr(transcript, 'text', ''),
            'words': [],
            'status': 'completed',
            'audio_url': audio_file,
            'language_code': getattr(transcript, 'language_code', 'en'),
        }
        
        # Add words with speaker labels
        if hasattr(transcript, 'words') and transcript.words:
            for word in transcript.words:
                word_data = {
                    'text': word.text,
                    'start': word.start,
                    'end': word.end,
                    'confidence': word.confidence,
                    'speaker': word.speaker if hasattr(word, 'speaker') else 'A'
                }
                transcript_data['words'].append(word_data)
        
        # Save main JSON
        with open(json_file, 'w') as f:
            json.dump(transcript_data, f, indent=2)
            
        # Save processed version (copy for compatibility)
        with open(processed_json, 'w') as f:
            json.dump(transcript_data, f, indent=2)
            
        elapsed = time.time() - start_time
        print(f"✅ Transcription completed in {elapsed:.1f}s")
        print(f"📄 Saved: {json_file}")
        print(f"📄 Saved: {processed_json}")
        
        # Step 2: Process into SRT and MD
        print("🔄 Generating output files...")
        words = transcript_data['words']
        
        if words:
            segments = group_words_into_segments(words)
            unique_speakers = len(set(word['speaker'] for word in words))
            
            write_srt(words, srt_file)
            write_md(words, md_file)
            
            print(f"📝 Generated: {srt_file}")
            print(f"📝 Generated: {md_file}")
            
            print(f"👥 Detected {unique_speakers} speakers, {len(segments)} fine segments (SRT), natural speaker turns (MD)")
        else:
            print("⚠️  No words with speaker data found")
        
        # Step 3: Organize files into folder
        print("🗂️  Organizing files...")
        organize_files_for_audio(audio_file, use_workbench=use_workbench)
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_video_preprocessor(specific_files=None):
    """Run video preprocessor to handle large video files"""
    preprocessor_path = os.path.join(os.path.dirname(__file__), 'video_preprocessor.py')
    if os.path.exists(preprocessor_path):
        print("🎬 Running video preprocessor...")
        try:
            cmd = ['python3', preprocessor_path]
            if specific_files:
                cmd.extend(specific_files)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.returncode != 0 and result.stderr:
                print(f"⚠️  Preprocessor warning: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Could not run video preprocessor: {e}")
    else:
        print("ℹ️  Video preprocessor not found, skipping video preprocessing")

def main():
    """Batch process all unprocessed MP3 files"""
    import sys
    
    print("🚀 AssemblyAI Batch Processing Pipeline")
    print("=" * 50)
    
    # Check if workbench exists
    if os.path.exists(INPUT_DIR):
        print(f"📂 Using workbench mode: {WORKBENCH_DIR}")
        print(f"   Input: {INPUT_DIR}")
        print(f"   Output: {OUTPUT_DIR}")
    else:
        print("📂 Using current directory mode")
    
    # Check if specific files were provided
    specific_files = sys.argv[1:] if len(sys.argv) > 1 else None
    video_files = []
    audio_files = []
    
    if specific_files:
        # Separate video and audio files
        for file in specific_files:
            if os.path.exists(file):
                ext = Path(file).suffix.lower()
                if ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']:
                    video_files.append(file)
                elif ext in ['.mp3', '.wav', '.m4a']:
                    audio_files.append(file)
                else:
                    print(f"⚠️  Unsupported file type: {file}")
            else:
                print(f"❌ File not found: {file}")
    
    # Run video preprocessor for video files
    if video_files:
        run_video_preprocessor(video_files)
        print("")  # Add spacing
        
        # After video preprocessing, add the extracted MP3 files to audio_files
        for video_file in video_files:
            base_name = get_base_filename(video_file)
            mp3_file = f"{base_name}.mp3"
            if os.path.exists(mp3_file) and mp3_file not in audio_files:
                audio_files.append(mp3_file)
                print(f"📄 Added extracted audio: {mp3_file}")
    elif not specific_files:
        # Run video preprocessor in batch mode
        run_video_preprocessor()
        print("")  # Add spacing
    
    # Setup API key
    try:
        setup_api_key()
        print("✅ API key configured")
    except Exception as e:
        print(f"❌ API key setup failed: {e}")
        return
    
    # Find unprocessed files
    if specific_files and audio_files:
        # Process specific audio files
        unprocessed = []
        for audio_file in audio_files:
            base_name = get_base_filename(audio_file)
            json_file = f"{base_name}.json"
            if not os.path.exists(json_file):
                unprocessed.append(audio_file)
    else:
        # Find all unprocessed MP3 files
        unprocessed = find_unprocessed_mp3_files()
    
    if not unprocessed:
        print("✨ No unprocessed MP3 files found")
        print("All files appear to be already processed")
        return
    
    print(f"📁 Found {len(unprocessed)} unprocessed MP3 files:")
    for file in unprocessed:
        print(f"   • {file}")
    
    # Process each file
    successful = 0
    failed = 0
    
    for mp3_file in unprocessed:
        if transcribe_and_process(mp3_file):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Total processed: {successful + failed}")

if __name__ == "__main__":
    main()