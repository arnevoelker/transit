import assemblyai as aai
import json
import os
import glob
import time
import shutil
from pathlib import Path

# Import the processor functions - we'll define them here to avoid import issues
import copy
import textwrap

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
    """
    if not words:
        return []
    
    segments = []
    start_time = words[0]['start']
    end_time = words[-1]['end']
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

def organize_files_for_audio(audio_file):
    """Organize all files related to an audio file into a folder"""
    base_name = get_base_filename(audio_file)
    folder_name = base_name
    
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
        if os.path.exists(pattern):
            related_files.append(pattern)
    
    if not related_files:
        print(f"⚠️  No related files found for {audio_file}")
        return False
    
    print(f"📁 Organizing files into folder: {folder_name}")
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"   ✅ Created folder: {folder_name}")
    
    # Move all related files
    moved_count = 0
    for file in related_files:
        destination = os.path.join(folder_name, file)
        
        if os.path.exists(destination):
            print(f"   ⚠️  File already exists in folder: {file}")
        else:
            try:
                shutil.move(file, destination)
                print(f"   📄 Moved: {file}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {file}: {e}")
    
    print(f"   ✅ Organized {moved_count} files into {folder_name}/")
    return True

def find_mp3_files():
    """Find all MP3 files in current directory"""
    return glob.glob("*.mp3")

def get_processed_files():
    """Get list of already processed files based on existing JSON files"""
    json_files = glob.glob("*.json")
    processed = set()
    for json_file in json_files:
        base_name = get_base_filename(json_file)
        processed.add(f"{base_name}.mp3")
    return processed

def transcribe_audio(audio_file, output_json):
    """Transcribe audio file using AssemblyAI"""
    print(f"Starting transcription of: {audio_file}")
    start_time = time.time()
    
    # Create transcriber with speaker diarization
    transcriber = aai.Transcriber()
    
    # Configure transcription with speaker labels and best model
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        format_text=True,
        punctuate=True,
        speech_model=aai.SpeechModel.best,
        language_detection=True,
    )
    
    try:
        # Submit audio for transcription
        transcript = transcriber.transcribe(audio_file, config=config)
        
        # Check for errors
        if transcript.error:
            print(f"Transcription error: {transcript.error}")
            return False
            
        # Save transcript data as JSON - use getattr for optional attributes
        transcript_data = {
            'id': getattr(transcript, 'id', 'unknown'),
            'text': getattr(transcript, 'text', ''),
            'words': [],
            'status': 'completed',
            'audio_url': audio_file,
            'language_code': getattr(transcript, 'language_code', 'en'),
        }
        
        # Add words with speaker labels if available
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
        
        # Save JSON file
        with open(output_json, 'w') as f:
            json.dump(transcript_data, f, indent=2)
            
        # Calculate processing time
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        print(f"Transcription completed in {minutes:02d}:{seconds:02d}")
        print(f"Saved to: {output_json}")
        return True
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return False

def rename_speakers_interactive(words):
    """Interactive speaker renaming with preview"""
    if not words:
        return {}
    
    # Group words into segments for better speaker preview
    segments = group_words_into_segments(words)
    
    # Find unique speakers and show examples
    speaker_examples = {}
    for segment in segments:
        speaker = segment['speaker']
        word_count = len(segment['text'].split())
        if speaker not in speaker_examples:
            speaker_examples[speaker] = {'first': segment, 'six_words': None}
        if word_count >= 6 and speaker_examples[speaker]['six_words'] is None:
            speaker_examples[speaker]['six_words'] = segment

    speakers = {}
    print(f"\nFound {len(speaker_examples)} speakers. Please provide names:")
    
    for speaker in speaker_examples:
        example_segment = speaker_examples[speaker]['six_words'] or speaker_examples[speaker]['first']
        timecode = milliseconds_to_hms(example_segment['start'])
        text = example_segment['text']
        print(f"\nSpeaker: {speaker}\nTime: {timecode}\nText: {text}")
        new_name = input(f'Enter a new name for {speaker} (or press Enter to keep "{speaker}"): ').strip()
        speakers[speaker] = new_name if new_name else speaker

    return speakers

def process_transcript(json_file, base_name):
    """Process transcript JSON to create SRT and MD files"""
    print(f"Processing transcript: {json_file}")
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        words = data.get('words', [])
        if not words:
            print("No words found in transcript")
            return False
            
        # Interactive speaker renaming
        speaker_mapping = rename_speakers_interactive(words)
        
        # Apply speaker name changes
        if speaker_mapping:
            for word in words:
                if word['speaker'] in speaker_mapping:
                    word['speaker'] = speaker_mapping[word['speaker']]
            
            # Save updated main JSON
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save processed version with new naming
            processed_json = f"{base_name} new_transcript_aai.json"
            with open(processed_json, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Updated speaker names in {json_file}")
            print(f"Saved processed version: {processed_json}")
        
        # Generate output files with new naming convention
        srt_file = f"{base_name} subtitle_aai.srt"
        md_file = f"{base_name} screenplay_aai.md"
        
        write_srt(words, srt_file)
        write_md(words, md_file)
        
        print(f"Generated: {srt_file}, {md_file}")
        
        # Organize files into folder
        print("🗂️  Organizing files...")
        organize_files_for_audio(base_name + ".mp3")  # Assume MP3 for organization
        
        return True
        
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        return False

def main():
    """Main pipeline function"""
    print("=== AssemblyAI Transcription & Processing Pipeline ===")
    
    # Setup API key
    try:
        setup_api_key()
    except Exception as e:
        print(f"API key setup failed: {e}")
        return
    
    # Find MP3 files
    mp3_files = find_mp3_files()
    if not mp3_files:
        print("No MP3 files found in current directory")
        return
    
    # Get already processed files
    processed_files = get_processed_files()
    
    # Process each MP3 file
    for mp3_file in mp3_files:
        if mp3_file in processed_files:
            print(f"Skipping {mp3_file} (already processed)")
            continue
            
        base_name = get_base_filename(mp3_file)
        json_file = f"{base_name}.json"
        
        print(f"\n{'='*50}")
        print(f"Processing: {mp3_file}")
        print(f"{'='*50}")
        
        # Step 1: Transcribe audio
        if transcribe_audio(mp3_file, json_file):
            # Step 2: Process transcript (speaker renaming + output generation)
            process_transcript(json_file, base_name)
        else:
            print(f"Failed to transcribe {mp3_file}")
    
    print("\nPipeline completed!")

if __name__ == "__main__":
    main()