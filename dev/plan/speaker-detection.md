# Speaker Detection System

## Overview

Intelligent speaker identification using multiple signals to reduce manual intervention while maintaining accuracy.

## Detection Methods

### Phase 1: Pattern Matching

**Filename Analysis:**
```
"20251104 WIR24 Rebecca x Arne.mp4"
→ Detected: ["Rebecca", "Arne"], Confidence: 0.85

"20251021 WIR24 Weekly.mp4"
→ Detected: ["Rebecca", "Arne", "Denise"], Confidence: 0.70
```

**Database Lookup:**
- Common participants per project
- Pre-defined meeting patterns
- Confidence scores

### Phase 2: Transcript Analysis (Future)
- Typical phrases per speaker
- Speaking style markers
- Role indicators

### Phase 3: Audio Profile Matching

**Voice Characteristics:**
- Compare speaker embeddings from AssemblyAI
- Calculate similarity with stored profiles
- Match to most similar known speaker

```python
def calculate_voice_similarity(
    new_embedding: np.array,
    stored_embedding: np.array
) -> float:
    # Cosine similarity
    similarity = np.dot(new_embedding, stored_embedding) / (
        np.linalg.norm(new_embedding) * 
        np.linalg.norm(stored_embedding)
    )
    return similarity
```

---

## Confidence Scoring

### Component Scores

| Signal | Weight | Max Score |
|--------|--------|-----------|
| Exact filename match | 0.60 | 0.60 |
| Partial filename match | 0.30 | 0.30 |
| Meeting type pattern | 0.20 | 0.20 |
| Speakers in database | 0.20 | 0.20 |
| Speaker count matches | 0.10 | 0.10 |
| Voice profile match (Phase 3+) | 0.30 | 0.30 |

### Decision Thresholds

- **Auto-Assign:** Confidence ≥ 0.80
- **Interactive:** Confidence < 0.80

### Examples

```python
# High Confidence (0.90)
"20251104 WIR24 Rebecca x Arne.mp4" + 2 speakers
→ AUTO-ASSIGN

# Medium Confidence (0.50)
"20251021 WIR24 Weekly.mp4" + 3 speakers
→ INTERACTIVE (with suggestions)

# Low Confidence (0.0)
"20251104 WIR24 Random Topic.mp4" + 2 speakers
→ INTERACTIVE (no suggestions)
```

---

## Audio Profile System

### Profile Collection

**When Created:**
1. After manual identification (100% verified)
2. After auto-assignment (verified by success)
3. During batch building from existing transcripts

**Quality Requirements:**
- Duration: 3-5 seconds
- Format: MP3, 64kbps, 16kHz mono
- Loudness: -16 LUFS (normalized)
- SNR: > 20 dB

### Storage Structure

```
config/audio_profiles/
├── arne_001.mp3
├── arne_002.mp3
├── rebecca_001.mp3
└── ...
```

### Database Integration

```json
{
  "speaker_profiles": {
    "Arne": {
      "audio_samples": [
        {
          "file": "audio_profiles/arne_001.mp3",
          "duration_ms": 3500,
          "source_file": "20251104 WIR24 Content Prototype...",
          "timestamp": "2024-11-04T17:30:15Z",
          "confidence": 1.0,
          "verified": true,
          "quality_score": 0.92
        }
      ]
    }
  }
}
```

---

## Detection Workflow

### Phase 1 Workflow

```
1. Extract filename hints
   → "rebecca.*arne" pattern found

2. Lookup in database
   → Pattern confidence: 0.85

3. Validate speakers
   → Both in common_participants ✓

4. Calculate confidence
   → Total: 0.90

5. Decision: AUTO-ASSIGN
   → A = Arne, B = Rebecca

6. Process & extract profiles
```

### Phase 3 Workflow (With Voice)

```
1. No filename pattern found

2. Get speaker embeddings from AssemblyAI

3. Match against voice profiles
   → Speaker A vs Arne: 0.92 similarity
   → Speaker B vs Rebecca: 0.89 similarity

4. Calculate confidence
   → Total: 0.85 (voice + database)

5. Decision: AUTO-ASSIGN

6. Extract new profiles (improve library)
```

---

## Error Handling

### Low Confidence
- Fall back to interactive mode
- Present suggestions if available
- Mark as verified (high quality profiles)

### Speaker Count Mismatch
- Lower confidence by 0.30
- Use detected speakers as suggestions
- Always fall back to interactive

### Unknown Speakers
- Add new speaker to database
- Extract profile with high priority
- Flag for review

---

## Monitoring

### Detection Metrics
```json
{
  "statistics": {
    "total_processed": 120,
    "auto_assigned": 105,
    "interactive_mode": 15,
    "auto_assign_rate": 0.875,
    "average_confidence": 0.82
  }
}
```

### Continuous Improvement
- Learn from corrections
- Adjust pattern confidence
- Review voice profiles
- Track accuracy over time

---

For detailed algorithms and code examples, see full speaker-detection documentation.
