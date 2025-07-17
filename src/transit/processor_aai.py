import json
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

def rename_speakers(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    
    # AssemblyAI format has words array at top level
    words = data.get('words', [])
    
    if not words:
        raise ValueError("Could not find words array in the AssemblyAI JSON file")

    # Group words into segments for better speaker preview
    segments = group_words_into_segments(words)
    
    speakers = {}
    new_data = copy.deepcopy(data)

    # Find the first segment with at least six words for each speaker
    speaker_examples = {}
    for segment in segments:
        speaker = segment['speaker']
        word_count = len(segment['text'].split())
        if speaker not in speaker_examples:
            speaker_examples[speaker] = {'first': segment, 'six_words': None}
        if word_count >= 6 and speaker_examples[speaker]['six_words'] is None:
            speaker_examples[speaker]['six_words'] = segment

    for speaker in speaker_examples:
        example_segment = speaker_examples[speaker]['six_words'] or speaker_examples[speaker]['first']
        timecode = milliseconds_to_hms(example_segment['start'])
        text = example_segment['text']
        print(f"\nSpeaker: {speaker}\nTime: {timecode}\nText: {text}")
        new_name = input(f'Enter a new name for {speaker} (shown above): ').strip()
        speakers[speaker] = new_name if new_name else speaker

    # Update speaker names in words array
    for word in new_data['words']:
        if word['speaker'] in speakers:
            word['speaker'] = speakers[word['speaker']]

    return new_data, segments

def write_new_data(new_data, file_name):
    with open(file_name, 'w') as file:
        json.dump(new_data, file, indent=2)

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

def write_md_natural(words, file_name):
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

def write_md(words, file_name):
    """Write Markdown file from AssemblyAI words data - natural speaker-turn format"""
    write_md_natural(words, file_name)

def main():
    # Default to the existing file, but allow command line argument
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else '20250625 WIR25 Biweekly.json'
    
    # Extract base name from input file
    base_name = input_file.replace('.json', '')
    
    # Generate output filenames with base name prepended
    new_json_file = f'{base_name} new_transcript_aai.json'
    srt_file = f'{base_name} subtitle_aai.srt'
    md_file = f'{base_name} screenplay_aai.md'

    print(f"Processing: {input_file}")
    print(f"Base name: {base_name}")

    # Step 1: Rename speakers and create new JSON
    new_data, segments = rename_speakers(input_file)
    write_new_data(new_data, new_json_file)

    # Step 2: Process the updated words to create SRT and MD files
    words = new_data.get('words', [])
    write_srt(words, srt_file)
    write_md(words, md_file)

    print(f"Processing complete. Output files: {new_json_file}, {srt_file}, {md_file}")

if __name__ == "__main__":
    main()