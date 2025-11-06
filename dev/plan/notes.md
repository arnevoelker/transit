# Development Notes

## Key Decisions Made

### Audio Snippet Storage
- **Decision:** Store 3-5 second audio samples with each speaker identification
- **Rationale:** Creates reference material for future voice recognition
- **Implementation:** Extract during processor_aai.py execution, save to audio_profiles/

### Background Service
- **Decision:** Use Python watchdog + macOS launchd
- **Rationale:** Reliable, native to macOS, easy to manage
- **Alternative Considered:** Cron (rejected - not continuous monitoring)

### Auto-Assign Threshold
- **Decision:** 80% confidence threshold
- **Rationale:** Balance between automation and accuracy
- **Fallback:** Interactive mode below 80%

### Notifications
- **Success:** Desktop notification (non-intrusive)
- **Failure:** Email alert (requires action)
- **Rationale:** Different urgency levels need different notification methods

## Technical Considerations

### File Size Limits
- Maximum video file size: ~2GB (AssemblyAI limit)
- Audio profile size: ~100KB per 3-second MP3
- Expected library growth: ~50MB for 500 profiles

### Processing Time
- Video → Audio extraction: ~60s for 1hr video
- Transcription: ~60s (AssemblyAI cloud processing)
- Enhancement: ~3s
- Total: ~2-3 minutes for 1hr meeting

### Database Growth
- speakers_db.json: ~10KB initially, grows slowly
- Audio profiles: ~100KB per speaker per file
- Expect ~5-10MB/month with regular usage

## Challenges & Solutions

### Challenge: File Copy Detection
**Problem:** Watcher might trigger while file is still copying
**Solution:** Debounce with file size stability check

### Challenge: Speaker Count Mismatch
**Problem:** Filename suggests 2 speakers, transcript has 3
**Solution:** Lower confidence, present as suggestions, fall back to interactive

### Challenge: Service Crashes
**Problem:** Daemon might crash and stop monitoring
**Solution:** launchd KeepAlive configuration auto-restarts

### Challenge: Multiple Files Simultaneously
**Problem:** Could overwhelm system resources
**Solution:** Queue management, process sequentially

## Future Enhancements Ideas

### Voice Recognition (Phase 4)
- Use AssemblyAI speaker embeddings
- Calculate cosine similarity with stored profiles
- Requires: numpy, voice embedding extraction
- Target: 95%+ accuracy

### Multi-Project Support
- Template for new projects
- Project-specific enhancement rules
- Shared speaker database across projects

### Advanced Analytics
- Dashboard showing processing stats
- Speaker appearance frequency
- Auto-detection success rates
- Processing time trends

### Integration Options
- Slack notifications
- Calendar integration (auto-schedule follow-ups)
- Notion/Obsidian automatic note creation
- Zapier webhooks

## Testing Strategy

### Unit Tests
- Each component tested independently
- Mock external dependencies (AssemblyAI, SMTP)
- pytest framework

### Integration Tests
- End-to-end pipeline
- Real file processing (with test files)
- Notification delivery

### Manual Testing
- Process real WIR24 meetings
- Verify speaker detection accuracy
- Check file organization
- Test error scenarios

## Deployment Checklist

### Pre-Deployment
- [ ] Backup existing transit codebase
- [ ] Document current manual workflow
- [ ] Create test files
- [ ] Set up test email account

### Phase 1
- [ ] Deploy orchestrator.py
- [ ] Update processor_aai.py
- [ ] Create speakers_db.json
- [ ] Test with 3-5 sample files
- [ ] Verify WIR24 enhancement

### Phase 2
- [ ] Deploy watcher.py
- [ ] Configure launchd service
- [ ] Set up email credentials
- [ ] Test notifications
- [ ] Monitor for 48 hours

### Phase 3
- [ ] Deploy audio_extractor.py
- [ ] Build initial profile library
- [ ] Test profile extraction
- [ ] Verify database updates

## Questions for User

1. **Email provider:** Confirm Gmail is okay for SMTP?
2. **Notification preferences:** Desktop notification sound?
3. **Error handling:** Retry failed files automatically or manual review?
4. **Archive policy:** Keep processed files in input folder or delete?
5. **Profile retention:** How many audio samples per speaker (10? 20? unlimited)?

## Resources

### Documentation
- Python watchdog: https://python-watchdog.readthedocs.io/
- launchd: https://www.launchd.info/
- AssemblyAI: https://www.assemblyai.com/docs

### Similar Projects
- (Add references to similar automation projects)

### Learning Materials
- (Add links to relevant tutorials)
