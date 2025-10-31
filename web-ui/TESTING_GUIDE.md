# 🧪 Web UI Testing Guide

Complete testing checklist for Jarvis X V2 Hybrid Web UI

---

## 🚀 Quick Test (5 minutes)

```bash
cd web-ui

# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Start frontend  
./start_frontend.sh

# Browser: Open http://localhost:3000
# Try all 3 themes!
```

---

## ✅ TESTING CHECKLIST

### **1. Backend API Tests**

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# System status
curl http://localhost:8000/system-status
# Expected: {"cpu_percent": X, "memory_percent": Y, ...}

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "mode": "casual"}'
# Expected: {"response": "...", "mode": "casual", ...}

# Modes list
curl http://localhost:8000/modes
# Expected: Array of 7 modes
```

### **2. WebSocket Tests**

```javascript
// Open browser console and run:
const ws = new WebSocket('ws://localhost:8000/ws/test-123')

ws.onopen = () => {
  console.log('✅ Connected')
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Test message',
    mode: 'casual'
  }))
}

ws.onmessage = (e) => {
  console.log('📨 Received:', JSON.parse(e.data))
}

// Expected: Response message from Jarvis
```

### **3. Theme Switching Tests**

**Professional Theme:**
- [ ] Clean white/dark background
- [ ] Rounded corners visible
- [ ] Smooth transitions
- [ ] Chat bubbles styled correctly
- [ ] Typography clear and modern

**Terminal Theme:**
- [ ] Pure black background
- [ ] Matrix green text
- [ ] Box-drawing characters visible (╔═╗)
- [ ] Monospace fonts everywhere
- [ ] Text glow effects
- [ ] Scanline effect (subtle)

**Avatar Theme:**
- [ ] Dark futuristic background
- [ ] Gradient effects visible
- [ ] Avatar appears in top-right
- [ ] Glass morphism panels
- [ ] Glow effects on buttons
- [ ] Smooth gradients

### **4. Avatar Tests (Avatar Theme Only)**

Enable Avatar theme, then:

- [ ] Avatar visible in top-right corner
- [ ] Eyes blink automatically (every 3-5 sec)
- [ ] Outer glow ring pulses
- [ ] Background particles float
- [ ] Avatar has blue/purple glow

**With TTS enabled:**
- [ ] Send message: "Hello Jarvis"
- [ ] Wait for TTS response
- [ ] Avatar mouth moves with audio
- [ ] Lip-sync is smooth (60fps)
- [ ] Thinking particles appear
- [ ] Mouth closes when audio ends

### **5. Feature Integration Tests**

**Mode Switching:**
- [ ] Click each of 7 modes
- [ ] Active mode highlights
- [ ] Mode name shows in header
- [ ] Messages show correct context

**System Monitoring:**
- [ ] CPU percentage updates
- [ ] Memory shows used/total
- [ ] Disk stats visible
- [ ] Updates every 2 seconds
- [ ] Progress bars animate
- [ ] Colors change (green < 60%, yellow < 80%, red >= 80%)

**TTS Controls:**
- [ ] Toggle TTS on/off in input box
- [ ] TTS button shows state (on/off)
- [ ] Enable TTS → responses are spoken
- [ ] Disable TTS → silent mode
- [ ] TTS status shows in header

**Settings Panel:**
- [ ] Opens with settings icon
- [ ] Theme buttons switch themes
- [ ] TTS toggle works
- [ ] Avatar toggle works (Avatar theme only)
- [ ] Settings persist after refresh

### **6. WebSocket Stability Tests**

- [ ] Connection established on load
- [ ] Messages sent successfully
- [ ] Responses received correctly
- [ ] Reconnects after backend restart
- [ ] Handles network interruption
- [ ] Ping/pong keep-alive works

### **7. Responsive Design Tests**

**Desktop (1920x1080):**
- [ ] Full layout visible
- [ ] Sidebar on left
- [ ] Chat in center
- [ ] Avatar in top-right
- [ ] No overflow issues

**Laptop (1366x768):**
- [ ] Layout adjusts
- [ ] All elements visible
- [ ] Scrolling works
- [ ] Avatar scales appropriately

**Tablet (768x1024):**
- [ ] Sidebar collapsible
- [ ] Touch-friendly buttons
- [ ] Readable fonts
- [ ] Avatar repositions

**Mobile (375x667):**
- [ ] Single column layout
- [ ] Sidebar as drawer
- [ ] Large touch targets
- [ ] Avatar hides or scales down

### **8. Performance Tests**

**Load Time:**
- [ ] Initial load < 2 seconds
- [ ] Theme switch < 100ms
- [ ] No lag when typing
- [ ] Smooth animations (60fps)

**Resource Usage:**
- [ ] RAM < 100MB total
- [ ] CPU < 10% idle
- [ ] No memory leaks
- [ ] No console errors

**Network:**
- [ ] WebSocket latency < 50ms
- [ ] API responses < 200ms
- [ ] Image loads instant
- [ ] Theme CSS loads instant

---

## 🐛 KNOWN ISSUES & FIXES

### **Issue: WebSocket won't connect**
**Fix:**
- Ensure backend is running
- Check port 8000 is available
- Verify firewall settings
- Try: `lsof -i :8000`

### **Issue: Lip-sync not working**
**Fix:**
- Must be in Avatar theme
- TTS must be enabled
- Check browser console for audio errors
- Verify browser supports Web Audio API
- Try Chrome/Edge (best support)

### **Issue: Theme not switching**
**Fix:**
- Check browser console for errors
- Clear localStorage: `localStorage.clear()`
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### **Issue: System stats not updating**
**Fix:**
- Check backend API is running
- Verify /system-status endpoint works
- Check browser network tab
- Ensure psutil is installed: `pip install psutil`

---

## 📊 EXPECTED RESULTS

### **All Tests Pass:**
```
✅ Backend: 6/6 endpoints working
✅ WebSocket: Connected and messaging
✅ Themes: 3/3 switching correctly
✅ Avatar: Visible and animated
✅ Lip-Sync: Working with TTS
✅ System Stats: Updating live
✅ Modes: All 7 functional
✅ Settings: Saving and loading
✅ Performance: <300KB, <60MB RAM
```

### **Demo Scenario:**

1. **Open UI** → Professional theme loads
2. **Send "Hello"** → Jarvis responds
3. **Switch to Terminal** → Matrix green aesthetic
4. **Switch to Avatar** → See animated avatar
5. **Enable TTS** → Jarvis speaks responses
6. **Watch avatar** → Mouth syncs with audio
7. **Change mode** → Engineer mode → Ask code question
8. **View stats** → See live CPU/RAM/Disk

**Result:** Fully functional multi-theme web UI! 🎉

---

## 🎯 SUCCESS CRITERIA

**Minimum Viable:**
- ✅ UI loads without errors
- ✅ Can send/receive messages
- ✅ At least 1 theme works
- ✅ WebSocket connects

**Fully Functional:**
- ✅ All 3 themes working
- ✅ Theme switching instant
- ✅ WebSocket stable
- ✅ System stats updating
- ✅ All 7 modes accessible

**Polished:**
- ✅ Avatar lip-sync working
- ✅ Smooth animations
- ✅ No console errors
- ✅ Mobile responsive
- ✅ Settings persist

---

**Start testing now!** 🚀

```bash
cd web-ui
./start_backend.sh &
./start_frontend.sh
```

