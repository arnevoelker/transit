#!/usr/bin/env python3
"""
Label Speakers - Interactive speaker relabeling for Transit transcripts

This tool allows you to rename speakers in existing transcripts.
It finds the latest transcript in your workbench/output folders and
lets you assign meaningful names to speakers (e.g., "John", "Sarah")
instead of the default labels (A, B, C, D).
"""

import json
import os
import glob
import copy
import textwrap
from pathlib import Path
from datetime import datetime

# Import shared functions from batch_process
from .batch_process import (
    milliseconds_to_hms, 
    milliseconds_to_srt_time,
    group_words_into_segments,
    write_srt,
    write_md,
    WORKBENCH_DIR,
    OUTPUT_DIR
)

def get_speaker_preview(words, speaker_label, num_samples=3, words_per_sample=20):
    """Get preview text samples for a specific speaker"""
    speaker_words = [w for w in words if w.get('speaker') == speaker_label]
    
    if not speaker_words:
        return []
    
    # Get evenly distributed samples
    total_words = len(speaker_words)
    if total_words <= words_per_sample:
        # If we have few words, just return all of them
        return [' '.join([w['text'] for w in speaker_words])]
    
    samples = []
    sample_positions = []
    
    if num_samples == 1:
        sample_positions = [0]
    else:
        # Calculate positions for even distribution
        step = (total_words - words_per_sample) // (num_samples - 1)
        sample_positions = [i * step for i in range(num_samples)]
    
    for pos in sample_positions:
        sample_words = speaker_words[pos:pos + words_per_sample]
        sample_text = ' '.join([w['text'] for w in sample_words])
        timestamp = milliseconds_to_hms(sample_words[0]['start'])
        samples.append(f"[{timestamp}] {sample_text}...")
    
    return samples

def find_latest_transcript(search_dir=None):
    """Find the most recently modified transcript JSON file"""
    if search_dir is None:
        # Default to workbench output if it exists
        if os.path.exists(OUTPUT_DIR):
            search_dir = OUTPUT_DIR
        else:
            search_dir = "."
    
    # Search for original transcript files (not processed versions)
    json_files = []
    
    if search_dir == OUTPUT_DIR:
        # Search in all output subdirectories
        pattern = os.path.join(search_dir, "*", "*.json")
        all_json_files = glob.glob(pattern)
        # Filter out processed versions
        json_files = [f for f in all_json_files if "new_transcript_aai" not in f]
    else:
        # Search in current directory
        all_json_files = glob.glob("*.json")
        json_files = [f for f in all_json_files if "new_transcript_aai" not in f]
    
    if not json_files:
        return None
    
    # Sort by modification time, newest first
    json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    return json_files[0]

def display_speaker_stats(words):
    """Display statistics about speakers in the transcript"""
    speaker_stats = {}
    
    for word in words:
        speaker = word.get('speaker', 'Unknown')
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                'word_count': 0,
                'duration_ms': 0,
                'first_timestamp': word['start'],
                'last_timestamp': word['end']
            }
        
        speaker_stats[speaker]['word_count'] += 1
        speaker_stats[speaker]['last_timestamp'] = word['end']
    
    print("\n📊 SPEAKER STATISTICS")
    print("=" * 50)
    
    for speaker, stats in sorted(speaker_stats.items()):
        duration_ms = stats['last_timestamp'] - stats['first_timestamp']
        duration_str = milliseconds_to_hms(duration_ms)
        word_count = stats['word_count']
        
        print(f"\nSpeaker {speaker}:")
        print(f"  Words spoken: {word_count:,}")
        print(f"  Speaking duration: {duration_str}")
        print(f"  First appears: {milliseconds_to_hms(stats['first_timestamp'])}")
    
    return speaker_stats

def interactive_speaker_rename(transcript_data):
    """Interactively rename speakers in the transcript"""
    words = transcript_data.get('words', [])
    if not words:
        print("❌ No words found in transcript")
        return None
    
    # Display speaker statistics
    speaker_stats = display_speaker_stats(words)
    unique_speakers = sorted(speaker_stats.keys())
    
    print(f"\n👥 Found {len(unique_speakers)} speakers: {', '.join(unique_speakers)}")
    
    # Show preview for each speaker and ask for new name
    speaker_mapping = {}
    
    print("\n🎤 SPEAKER IDENTIFICATION")
    print("=" * 50)
    print("For each speaker, you'll see sample text to help identify them.")
    print("Enter a name (or press Enter to keep the default label)")
    print("=" * 50)
    
    for speaker in unique_speakers:
        print(f"\n--- Speaker {speaker} ---")
        
        # Get and display preview samples
        samples = get_speaker_preview(words, speaker, num_samples=3)
        for sample in samples:
            print(f"  {sample}")
        
        # Ask for new name
        new_name = input(f"\nNew name for Speaker {speaker} (or Enter to keep '{speaker}'): ").strip()
        
        if new_name:
            speaker_mapping[speaker] = new_name
            print(f"✅ Speaker {speaker} → {new_name}")
        else:
            speaker_mapping[speaker] = speaker
            print(f"✅ Keeping Speaker {speaker}")
    
    # Apply speaker mapping to create new transcript
    new_data = copy.deepcopy(transcript_data)
    
    # Update words with new speaker names
    for word in new_data.get('words', []):
        old_speaker = word.get('speaker')
        if old_speaker in speaker_mapping:
            word['speaker'] = speaker_mapping[old_speaker]
    
    # Update the main text if needed (though this is usually just the raw text)
    # The speaker labels are primarily in the words array
    
    return new_data, speaker_mapping

def process_transcript(json_file):
    """Process a transcript file with speaker relabeling"""
    base_name = Path(json_file).stem
    output_dir = os.path.dirname(json_file)
    
    # Generate output filenames
    new_json_file = os.path.join(output_dir, f"{base_name} new_transcript_aai.json")
    srt_file = os.path.join(output_dir, f"{base_name} subtitle_aai.srt")
    md_file = os.path.join(output_dir, f"{base_name} screenplay_aai.md")
    
    print(f"\n📄 Processing: {json_file}")
    
    # Load transcript data
    try:
        with open(json_file, 'r') as f:
            transcript_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Interactive speaker renaming
    result = interactive_speaker_rename(transcript_data)
    if result is None:
        return False
    
    new_data, speaker_mapping = result
    
    # Save the new transcript
    try:
        with open(new_json_file, 'w') as f:
            json.dump(new_data, f, indent=2)
        print(f"\n✅ Saved relabeled transcript: {new_json_file}")
    except Exception as e:
        print(f"❌ Error saving new transcript: {e}")
        return False
    
    # Generate SRT and MD files with new speaker names
    words = new_data.get('words', [])
    if words:
        try:
            write_srt(words, srt_file)
            write_md(words, md_file)
            print(f"📝 Generated: {srt_file}")
            print(f"📝 Generated: {md_file}")
        except Exception as e:
            print(f"⚠️  Error generating output files: {e}")
    
    # Show summary
    print("\n📊 RELABELING SUMMARY")
    print("=" * 50)
    for old_name, new_name in speaker_mapping.items():
        if old_name != new_name:
            print(f"  {old_name} → {new_name}")
    
    return True

def main():
    """Main function for speaker labeling"""
    print("🏷️  Transit Speaker Labeling Tool")
    print("=" * 50)
    
    import sys
    
    # Check if a specific file was provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        if not os.path.exists(json_file):
            print(f"❌ File not found: {json_file}")
            return
    else:
        # Find the latest transcript
        print("🔍 Searching for latest transcript...")
        json_file = find_latest_transcript()
        
        if not json_file:
            print("❌ No transcript files found")
            print("\nTip: Run this from your project directory or specify a JSON file:")
            print("  python -m src.transit.label_speakers transcript.json")
            return
        
        # Ask for confirmation
        file_path = os.path.relpath(json_file)
        print(f"\n📄 Found: {file_path}")
        print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime(json_file)).strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = input("\nDo you want to reprocess this file for speaker labeling? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled")
            return
    
    # Process the transcript
    success = process_transcript(json_file)
    
    if success:
        print("\n✨ Speaker labeling complete!")
    else:
        print("\n❌ Speaker labeling failed")

if __name__ == "__main__":
    main()