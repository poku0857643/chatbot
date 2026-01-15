# Screenshots

Add your screenshots here:

1. **desktop-chat.png** - Main chat interface on desktop
2. **mobile-chat.png** - Mobile responsive view
3. **file-upload.png** - File upload feature
4. **rag-response.png** - AI response with document context
5. **streaming-demo.gif** - Animated GIF of streaming responses (optional)

## How to Take Good Screenshots

### Desktop (1920x1080 recommended)
1. Open http://localhost:5173
2. Upload a sample document
3. Ask a question to demonstrate RAG
4. Capture the streaming response

### Mobile (375x667 - iPhone SE size)
1. Use browser DevTools (Cmd+Opt+I on Mac)
2. Toggle device toolbar (Cmd+Shift+M)
3. Select iPhone SE or similar
4. Take screenshots

### Tools
- macOS: Cmd+Shift+4 (select area)
- Windows: Snipping Tool
- Chrome: Full page screenshot in DevTools
- Screen recording: QuickTime (Mac) / OBS Studio (cross-platform)

## Creating an Animated GIF
```bash
# Using ffmpeg
ffmpeg -i screen-recording.mov -vf "fps=10,scale=800:-1" streaming-demo.gif
```
