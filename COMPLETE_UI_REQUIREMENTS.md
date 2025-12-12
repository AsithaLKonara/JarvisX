# 📋 Complete UI Requirements - JarvisX V2

## Document Information
- **Version:** 2.0
- **Last Updated:** January 2025
- **Status:** Updated - New Design Direction
- **Design System:** Multi-Platform Design System
  - **Web Landing/Dashboard:** n8n-style (clean, professional, light)
  - **Web Chat:** ChatGPT-style (sidebar-based, dark chat interface)
  - **Mobile/Desktop:** Siri-style (compact, voice-first interface)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Design System](#design-system)
3. [Platform Requirements](#platform-requirements)
4. [Component Specifications](#component-specifications)
5. [User Flows](#user-flows)
6. [Accessibility Requirements](#accessibility-requirements)
7. [Responsive Design](#responsive-design)
8. [Animation & Interactions](#animation--interactions)
9. [Integration Requirements](#integration-requirements)
10. [Performance Requirements](#performance-requirements)
11. [Testing Requirements](#testing-requirements)

---

## Executive Summary

JarvisX V2 requires a modern, platform-optimized UI across **4 platforms** (Web, Mobile, Desktop, CLI) using platform-specific design systems:
- **Web Landing/Dashboard:** n8n-style clean professional design (light backgrounds, professional colors)
- **Web Chat Interface:** ChatGPT-style sidebar-based chat (dark sidebar, clean message interface)
- **Mobile/Desktop:** Siri-style compact voice-first interface (minimal UI, large voice controls)

The UI must support real-time chat, voice interaction, authentication, and seamless integration with the AI backend.

### Key Principles
- **Platform Optimization:** Design tailored to each platform's strengths
- **Accessibility:** WCAG 2.1 AA compliance across all platforms
- **Performance:** Sub-100ms interaction feedback, smooth 60fps animations
- **Responsiveness:** Support from 320px mobile to 4K desktop displays
- **Modern Aesthetics:** Clean, professional designs optimized for user experience

---

## Design System

**Note:** This document now reflects the updated multi-platform design approach. For detailed design tokens, see `web-app/styles/design-tokens.css`.

### 1. Color Palette

#### Web Platform (n8n-style - Landing/Dashboard)
```css
/* Primary Colors */
--web-primary: #6366f1;
--web-primary-hover: #4f46e5;
--web-background: #ffffff;
--web-surface: #f9fafb;

/* Text Colors */
--web-text-primary: #1f2937;
--web-text-secondary: #6b7280;
--web-text-tertiary: #9ca3af;

/* Status Colors */
--web-success: #10b981;
--web-error: #ef4444;
--web-warning: #f59e0b;
--web-info: #3b82f6;
```

#### Web Chat Interface (ChatGPT-style)
```css
/* Chat Colors */
--chat-sidebar-bg: #202123;
--chat-main-bg: #343541;
--chat-main-text: #ffffff;
--chat-input-bg: #40414f;
```

#### Mobile/Desktop (Siri-style)
```css
/* Siri-style Colors */
--siri-bg: #000000;
--siri-text: #ffffff;
--siri-voice-button: #ffffff;
--siri-voice-button-active: #ff3b30;
```

**Full token definitions:** See `web-app/styles/design-tokens.css` for complete design token system.

### 2. Typography

#### Font Families
```css
/* Headings */
--font-heading: 'Alata', sans-serif;

/* Body Text */
--font-body: 'Albert Sans', sans-serif;
```

#### Font Scale
```
Heading 1 (H1): 32px / 48px line-height / Alata / Bold
Heading 2 (H2): 24px / 36px line-height / Alata / Bold
Heading 3 (H3): 22px / 33px line-height / Alata / Regular
Heading 4 (H4): 18px / 27px line-height / Alata / Regular

Body Large: 16px / 24px line-height / Albert Sans / Regular
Body: 14px / 21px line-height / Albert Sans / Regular
Body Small: 12px / 18px line-height / Albert Sans / Regular
Caption: 11px / 16px line-height / Albert Sans / Regular
```

#### Font Weights
- Regular: 400
- Medium: 500
- Semi-bold: 600
- Bold: 700

### 3. Spacing System

```
Base Unit: 4px

Scale:
  xs: 4px   (0.25rem)
  sm: 8px   (0.5rem)
  md: 12px  (0.75rem)
  base: 16px (1rem)
  lg: 24px  (1.5rem)
  xl: 32px  (2rem)
  2xl: 48px (3rem)
  3xl: 64px (4rem)
```

### 4. Border Radius

```
Small: 8px
Medium: 12px
Large: 20px
Pill: 1000px (for buttons)
Circle: 50%
```

### 5. Shadows & Effects

#### Glass Morphism
```css
.glass-panel {
  background: rgba(0, 0, 0, 0.001);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.25),              /* Outer shadow */
    inset 3px 3px 9.8px rgba(255, 255, 255, 0.19), /* Inner highlight */
    inset -4px -4px 5.7px rgba(0, 0, 0, 0.25);    /* Inner shadow */
}
```

#### Drop Shadows
- **Light:** `0 2px 8px rgba(0, 0, 0, 0.15)`
- **Medium:** `0 4px 12px rgba(0, 0, 0, 0.25)`
- **Heavy:** `0 8px 24px rgba(0, 0, 0, 0.35)`

### 6. Gradients

#### Primary Gradient
```css
background: linear-gradient(
  135deg,
  #000000 0%,      /* Primary Blue (Black) */
  #000000 50%,     /* Primary Aqua (Black) */
  #A855F7 100%     /* Primary Purple */
);
background-size: 200% 200%;
animation: gradient-shift 5s ease infinite;
```

#### Gradient Blob (Avatar)
- Multiple layered gradients with blur effects
- Animated color transitions
- Radial and linear gradient combinations
- Opacity variations (0.4 - 1.0)

---

## Platform Requirements

### 1. Web Application (Next.js)

#### Technology Stack
- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **State:** React Hooks + Context API
- **Real-time:** WebSocket

#### Screen Requirements

##### 1.1 Landing Page
- **Layout:** Full-screen gradient background
- **Content:**
  - Hero section with animated gradient blob
  - Feature highlights (3-4 cards)
  - Call-to-action buttons (Login/Register)
  - Navigation header (minimal)
- **Responsive:** Mobile-first, scales to desktop
- **Animations:** Fade-in on scroll, gradient animations

##### 1.2 Authentication Pages

**Login Page:**
- **Layout:** Centered form on gradient background
- **Components:**
  - Email/password input fields (glass style)
  - "Remember me" checkbox
  - Login button (primary)
  - "Forgot password?" link
  - OAuth buttons (Google, Apple, Facebook)
  - Sign up link
- **Validation:** Real-time validation with error messages
- **States:** Default, focus, error, loading, success

**Register Page:**
- **Layout:** Similar to login, additional fields
- **Components:**
  - Name input
  - Email input
  - Password input (with strength indicator)
  - Confirm password input
  - Terms & conditions checkbox
  - Register button
  - OAuth options
  - Login link

**OAuth Callback:**
- **Layout:** Loading state with spinner
- **Functionality:** Handles OAuth redirect and token storage

##### 1.3 Chat Interface

**Layout:**
- **Dimensions:** 
  - Mobile: Full viewport (267px min width)
  - Desktop: Max-width 768px, centered
  - Height: 585px (or viewport height - header/footer)

**Header Section:**
- **Elements:**
  - Greeting: "Hi, [Username]" (text-white/80, Alata 16px)
  - Prompt: "Say something" (text-white, Alata 22px)
  - Close button (top-right, glass button style)
- **Border:** Bottom border (white/10 opacity)

**Avatar Section:**
- **Component:** Gradient blob (175x175px)
- **Position:** Centered, with vertical padding
- **Animation:** Subtle pulse/breathing effect

**Description Section:**
- **Text:** Project description (text-white/80, Albert Sans 14px)
- **Padding:** Horizontal 16px, bottom 16px
- **Line height:** 18px

**Messages Area:**
- **Layout:** Scrollable container (flex-1, overflow-y-auto)
- **Spacing:** 16px vertical spacing between messages
- **Empty State:** Centered text "Start a conversation with JarvisX"
- **Loading State:** Animated dots (3 dots, staggered bounce)
- **Auto-scroll:** Smooth scroll to bottom on new message

**Message Bubbles:**
- **User Message:**
  - Alignment: Right
  - Background: Glass panel with slight purple tint
  - Text: White
  - Max-width: 70% of container
  - Border radius: 12px (rounded on left side)
  
- **Assistant Message:**
  - Alignment: Left
  - Background: Glass panel
  - Text: White
  - Max-width: 70% of container
  - Border radius: 12px (rounded on right side)

**Input Area:**
- **Layout:** Fixed bottom, border-top (white/10)
- **Components:**
  - Text input (multiline, glass style)
  - Voice button (microphone icon)
  - Send button (glass button, disabled when empty)
- **Placeholder:** "Type your message..."
- **States:** Default, focus, typing, disabled

##### 1.4 Navigation

**Layout:**
- **Position:** Top bar (fixed or sticky)
- **Components:**
  - Logo/Brand name (left)
  - User menu (right)
  - Mode switcher (if applicable)
- **Style:** Glass panel, minimal border

**User Menu:**
- **Trigger:** User avatar or name
- **Dropdown:**
  - Profile link
  - Settings link
  - Logout button
  - Glass panel style

#### Responsive Breakpoints
```
Mobile: 320px - 640px
Tablet: 641px - 1024px
Desktop: 1025px - 1920px
Large Desktop: 1921px+
```

#### Browser Support
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Mobile

---

### 2. Mobile Application (React Native)

#### Technology Stack
- **Framework:** React Native (Expo)
- **Styling:** StyleSheet API + custom glass utilities
- **Animation:** React Native Reanimated / Animated API
- **Navigation:** React Navigation
- **State:** React Hooks + Context API

#### Screen Requirements

##### 2.1 Landing Screen
- **Layout:** Full-screen with gradient background
- **Components:** Similar to web, optimized for touch
- **Touch Targets:** Minimum 44x44px

##### 2.2 Authentication Screens
- **Layout:** Full-screen forms
- **Keyboard Handling:** KeyboardAvoidingView
- **Input Fields:** Native TextInput with glass styling
- **OAuth:** Native OAuth flows (expo-auth-session)

##### 2.3 Chat Screen

**Layout:**
- **Structure:** 
  - Header (fixed)
  - Messages area (scrollable)
  - Input bar (fixed bottom, above keyboard)

**Chat Container:**
- **Dimensions:** Full viewport
- **Keyboard Handling:** KeyboardAvoidingView with padding
- **Scroll:** ScrollView with auto-scroll to bottom

**Message Bubbles:**
- **Styling:** Similar to web, native components
- **Touch:** Long-press for options (copy, delete)

**Input Bar:**
- **Layout:** Horizontal layout
- **Components:**
  - Text input (flex-1)
  - Microphone button (voice input)
  - Send button
- **Keyboard:** Dismiss on send

**Floating Chat Widget:**
- **Position:** Bottom-right corner
- **Size:** 56x56px circular button
- **State:** Collapsed (button) / Expanded (chat window)
- **Animation:** Scale and slide animations
- **Glass style:** Circular glass button

##### 2.4 Navigation

**Tab Navigation (if applicable):**
- **Tabs:** Chat, History, Settings, Profile
- **Style:** Glass bottom tab bar
- **Icons:** Custom icons with active/inactive states

**Stack Navigation:**
- **Transitions:** Slide transitions
- **Header:** Glass style header with back button

#### Platform-Specific Requirements

**iOS:**
- Safe area insets handling
- Haptic feedback on interactions
- Native navigation gestures
- Status bar: Light content

**Android:**
- Status bar: Light content
- Back button handling
- Material Design touch feedback (optional)
- Edge-to-edge display support

#### Device Support
- **iOS:** iOS 13+
- **Android:** Android 8.0 (API 26)+
- **Screen Sizes:** 4" to 7" devices

---

### 3. Desktop Application (PyQt6)

#### Technology Stack
- **Framework:** PyQt6
- **Styling:** QSS (Qt Style Sheets)
- **Window:** Frameless window with custom title bar
- **System Integration:** System tray

#### Window Requirements

##### 3.1 Main Window

**Window Properties:**
- **Style:** Frameless, resizable
- **Minimum Size:** 400x600px
- **Default Size:** 500x700px
- **Background:** Black (#000000)

**Custom Title Bar:**
- **Height:** 40px
- **Components:**
  - App icon/name (left)
  - Window controls: Minimize, Maximize, Close (right)
- **Style:** Glass panel
- **Draggable:** Yes (for window movement)

##### 3.2 Chat Widget

**Layout:**
- **Structure:** Similar to web/mobile
- **Components:**
  - Header section
  - Messages area (QScrollArea)
  - Input section

**Styling:**
- **Glass Effect:** Implemented via QSS with backdrop-filter (if supported)
- **Fallback:** Semi-transparent backgrounds with blur simulation
- **Colors:** Match web color palette

**Input:**
- **Component:** QLineEdit or QTextEdit (multiline)
- **Placeholder:** "Type your message..."
- **Shortcuts:** Enter to send, Shift+Enter for new line

##### 3.3 System Tray Integration

**Tray Icon:**
- **Icon:** App icon (16x16, 32x32)
- **Menu:**
  - Show/Hide window
  - Open chat
  - Settings
  - Quit
- **Actions:**
  - Click: Toggle window visibility
  - Right-click: Show context menu

##### 3.4 Window States

**Normal:**
- Standard window with title bar

**Minimized:**
- Hide to system tray

**Maximized:**
- Full-screen with window controls

**Always on Top:**
- Optional setting to keep window above others

#### Platform-Specific Requirements

**Windows:**
- Native window controls styling
- Taskbar integration
- Notification support

**macOS:**
- Traffic light window controls
- Menu bar integration
- Dock icon behavior

**Linux:**
- Window manager integration
- System tray support (varies by DE)

---

### 4. CLI Interface

#### Terminal Requirements

**Color Scheme:**
- **Background:** Black (#000000)
- **Text:** White (#FFFFFF)
- **Accents:** Purple (#A855F7)

**Typography:**
- **Font:** Monospace font (user's terminal preference)
- **Size:** User's terminal settings

**Layout:**
- **Prompt:** `jarvisx > ` or `jarvisx [mode] > `
- **Status Indicators:** Color-coded status messages
- **Progress Bars:** ASCII/Unicode progress indicators

**Interactive Elements:**
- **Input:** Standard terminal input with history
- **Suggestions:** Tab completion
- **Output:** Formatted text with colors and icons
- **Tables:** ASCII tables for structured data

**Visual Feedback:**
- **Loading:** Spinner animations
- **Success:** Green checkmark (✓)
- **Error:** Red X (✗)
- **Info:** Blue info icon (ℹ)

---

## Component Specifications

### 1. GlassContainer Component

**Purpose:** Base container with glass morphism effect

**Variants:**
- `panel`: Main content panel
- `button`: Interactive button
- `card`: Content card

**Props:**
```typescript
{
  variant?: 'panel' | 'button' | 'card'
  className?: string
  onClick?: () => void
  children: React.ReactNode
}
```

**Styles:**
- Backdrop blur: 20px
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border radius: 12px (panel/card), 20px (button)
- Shadows: Multiple layered shadows
- Background: rgba(0, 0, 0, 0.001)

**Interactions:**
- Button variant: Hover scale (1.05), active scale (0.95)
- Transition: 0.3s ease

---

### 2. GradientBlob Component

**Purpose:** Animated gradient blob for avatar/visual interest

**Props:**
```typescript
{
  size?: number  // Default: 175
  className?: string
}
```

**Visual Properties:**
- Size: 175x175px (default)
- Multiple layered gradients
- Blur effects (layer blur: 200px)
- Animated color transitions
- Circular shape

**Animation:**
- Subtle pulse/breathing effect
- Gradient position animation
- Opacity variations

---

### 3. MessageBubble Component

**Purpose:** Display chat messages

**Props:**
```typescript
{
  message: string
  role: 'user' | 'assistant'
  timestamp?: Date
}
```

**Styles by Role:**

**User Message:**
- Alignment: Right
- Background: Glass panel with purple tint
- Text: White
- Border radius: 12px (more rounded on left)

**Assistant Message:**
- Alignment: Left
- Background: Glass panel
- Text: White
- Border radius: 12px (more rounded on right)

**Common:**
- Max-width: 70% of container
- Padding: 12px 16px
- Margin: 8px 0
- Word wrap: Enabled

---

### 4. ChatInput Component

**Purpose:** Text input for chat messages

**Props:**
```typescript
{
  onSend: (message: string) => void
  placeholder?: string
  disabled?: boolean
}
```

**Features:**
- Multiline input
- Placeholder text
- Send button (enabled when text entered)
- Voice input button (optional)
- Character counter (optional, for long messages)
- Enter to send, Shift+Enter for new line

**States:**
- Default: Empty input, send disabled
- Typing: Input has content, send enabled
- Sending: Loading state, input disabled
- Error: Error message displayed

**Styling:**
- Glass panel background
- White text
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border radius: 12px
- Padding: 12px 16px

---

### 5. MicrophoneButton Component

**Purpose:** Voice input trigger

**Props:**
```typescript
{
  onRecordStart: () => void
  onRecordStop: () => void
  disabled?: boolean
}
```

**Visual States:**
- **Idle:** Static microphone icon
- **Listening:** Animated pulse, red indicator
- **Processing:** Spinner animation
- **Disabled:** Grayed out

**Styling:**
- Circular button (54x54px)
- Glass container with border
- Icon: Microphone (32x32px)
- Active state: Purple accent border

---

### 6. Button Component

**Variants:**
- `primary`: Main action (purple accent)
- `secondary`: Secondary action (glass style)
- `ghost`: Text-only button
- `icon`: Icon-only button

**Sizes:**
- `sm`: 32px height
- `md`: 40px height
- `lg`: 48px height

**States:**
- Default
- Hover (scale 1.05, lighter background)
- Active (scale 0.95)
- Disabled (50% opacity, no interaction)
- Loading (spinner icon)

---

### 7. Input Component

**Types:**
- Text
- Email
- Password
- Textarea (multiline)

**Features:**
- Label (optional)
- Placeholder
- Helper text
- Error message
- Icon (prefix/suffix, optional)

**States:**
- Default
- Focus (border highlight, glow)
- Error (red border, error message)
- Disabled
- Read-only

**Styling:**
- Glass panel background
- White text
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border radius: 12px
- Padding: 12px 16px

---

### 8. Modal/Dialog Component

**Purpose:** Overlay dialogs for confirmations, forms, etc.

**Features:**
- Backdrop (dark overlay with blur)
- Centered content
- Close button (X icon, top-right)
- Escape key to close
- Click outside to close (optional)

**Styling:**
- Content: Glass panel
- Max-width: 500px
- Padding: 24px
- Border radius: 16px

---

### 9. Loading Spinner Component

**Variants:**
- Dots (3 animated dots)
- Circle (rotating circle)
- Pulse (expanding circle)

**Sizes:**
- `sm`: 16px
- `md`: 24px
- `lg`: 32px

**Colors:**
- Default: White
- Primary: Purple (#A855F7)

---

### 10. Toast/Notification Component

**Purpose:** Temporary notifications

**Types:**
- Success (green)
- Error (red)
- Warning (amber)
- Info (blue)

**Position:**
- Top-right (default)
- Top-center
- Bottom-right
- Bottom-center

**Duration:**
- Default: 5 seconds
- Auto-dismiss
- Manual dismiss (X button)

**Styling:**
- Glass panel
- Icon + message
- Border-left accent (color by type)
- Slide-in animation
- Fade-out on dismiss

---

## User Flows

### 1. Authentication Flow

**Landing Page → Login/Register → Dashboard/Chat**

1. User lands on homepage
2. Clicks "Login" or "Register"
3. Enters credentials (or uses OAuth)
4. Redirected to chat interface
5. Session stored (JWT tokens)

**Error Handling:**
- Invalid credentials: Error message below form
- Network error: Toast notification
- OAuth error: Redirect with error message

---

### 2. Chat Flow

**Empty State → Conversation → History**

1. User opens chat interface
2. Sees empty state with avatar and description
3. Types message or uses voice input
4. Message sent, loading indicator shown
5. Response received, displayed in chat
6. Conversation continues

**Features:**
- Message history persists
- Auto-scroll to latest message
- Typing indicators (optional)
- Message timestamps
- Copy message (long-press on mobile)

---

### 3. Voice Input Flow

**Idle → Listening → Processing → Response**

1. User clicks microphone button
2. Recording starts (visual feedback: pulse animation)
3. User speaks
4. User stops recording (or auto-stop after silence)
5. Audio processed, converted to text
6. Text sent as message
7. Response displayed

**Error Handling:**
- No microphone permission: Permission request modal
- Recording error: Error toast
- Recognition error: Error message, allow retry

---

### 4. Mode Switching Flow

**Current Mode → Mode Selector → New Mode**

1. User accesses mode selector (via menu or command)
2. Sees available modes:
   - Engineer Mode
   - System Monitor
   - Designer Mode
   - Editor Mode
   - Business Mode
   - Casual/Sinhala
   - Career Assistant
3. Selects mode
4. UI updates (if applicable)
5. Chat context switches to selected mode

**Visual Feedback:**
- Mode indicator in header/navigation
- Optional: Mode-specific color accent

---

### 5. Settings Flow

**Profile → Settings → Update → Save**

1. User opens settings/profile
2. Sees current settings:
   - Profile information
   - Preferences (theme, language, etc.)
   - Voice settings
   - Notification settings
   - Account settings
3. Makes changes
4. Saves changes
5. Success feedback (toast or message)

---

## Accessibility Requirements

### 1. WCAG 2.1 AA Compliance

**Color Contrast:**
- Text on background: Minimum 4.5:1 (normal text), 3:1 (large text)
- Interactive elements: Minimum 3:1 contrast
- Focus indicators: Clear, visible (3px outline)

**Keyboard Navigation:**
- All interactive elements keyboard accessible
- Logical tab order
- Skip links for main content
- Keyboard shortcuts documented

**Screen Readers:**
- Semantic HTML/ARIA labels
- Alt text for images/icons
- Form labels associated with inputs
- Status announcements (ARIA live regions)

**Focus Management:**
- Visible focus indicators (purple outline, 3px)
- Focus trap in modals
- Focus restoration on modal close

### 2. Platform-Specific Accessibility

**Web:**
- ARIA roles and properties
- Semantic HTML5 elements
- Focus-visible pseudo-class

**Mobile:**
- Accessibility labels (iOS: accessibilityLabel, Android: contentDescription)
- Touch target size: Minimum 44x44px
- Haptic feedback for important actions

**Desktop:**
- Keyboard shortcuts
- Screen reader support (platform-specific APIs)
- High contrast mode support

### 3. Responsive Text

- Minimum font size: 12px (body), 14px (buttons)
- Scalable text (rem/em units)
- User can zoom to 200% without horizontal scrolling

### 4. Motion/Animation

- Respect `prefers-reduced-motion`
- Disable animations for users who prefer reduced motion
- Critical animations: Max 5 seconds

---

## Responsive Design

### 1. Breakpoint Strategy

**Mobile First Approach:**
- Base styles for mobile (320px+)
- Progressive enhancement for larger screens
- Flexible layouts (flexbox/grid)

**Breakpoints:**
```
Mobile:    320px - 640px
Tablet:    641px - 1024px
Desktop:   1025px - 1920px
Large:     1921px+
```

### 2. Layout Adaptations

**Mobile (< 640px):**
- Single column layout
- Full-width components
- Stacked navigation
- Bottom sheet modals
- Full-screen chat

**Tablet (641px - 1024px):**
- Two-column layout (optional)
- Side navigation (collapsible)
- Larger touch targets
- Modal dialogs (centered)

**Desktop (1025px+):**
- Multi-column layouts
- Persistent side navigation
- Hover states enabled
- Larger spacing
- Max-width containers (for readability)

### 3. Component Adaptations

**Chat Interface:**
- Mobile: Full viewport height
- Tablet: 80% viewport height, centered
- Desktop: Fixed height (585px) or max-height

**Navigation:**
- Mobile: Bottom tab bar or hamburger menu
- Tablet: Side navigation (collapsible)
- Desktop: Top bar or side navigation

**Forms:**
- Mobile: Single column, full-width inputs
- Desktop: Two-column (where appropriate), max-width forms

### 4. Touch vs Mouse

**Touch Devices:**
- Larger touch targets (44x44px minimum)
- Swipe gestures
- Pull-to-refresh (where applicable)

**Mouse Devices:**
- Hover states
- Right-click context menus
- Precise cursor interactions

---

## Animation & Interactions

### 1. Animation Principles

**Duration:**
- Micro-interactions: 150-200ms
- Standard transitions: 300ms
- Page transitions: 400-500ms
- Loading states: Continuous until completion

**Easing:**
- Standard: `ease` or `ease-in-out`
- Entrance: `ease-out`
- Exit: `ease-in`
- Bounce: Custom cubic-bezier for playful effects

**Performance:**
- Use CSS transforms (translate, scale, rotate) for animations
- Avoid animating layout properties (width, height, margin)
- GPU acceleration (transform: translateZ(0) or will-change)

### 2. Page Transitions

**Route Changes:**
- Fade: 300ms fade in/out
- Slide: Horizontal slide (mobile), fade (desktop)
- No animation: Instant (for programmatic navigation)

### 3. Component Animations

**Buttons:**
- Hover: Scale 1.05, 200ms
- Active: Scale 0.95, 150ms
- Disabled: Fade to 50% opacity, 200ms

**Modals:**
- Entrance: Scale 0.95 → 1.0, fade in, 300ms
- Exit: Scale 1.0 → 0.95, fade out, 200ms
- Backdrop: Fade in/out, 300ms

**Message Bubbles:**
- Entrance: Slide in from bottom, fade in, 300ms
- Stagger: 50ms delay between multiple messages

**Loading States:**
- Spinner: Continuous rotation, 1s linear infinite
- Dots: Bounce animation, staggered delays
- Skeleton: Shimmer effect, 1.5s ease-in-out infinite

### 4. Micro-interactions

**Input Focus:**
- Border color transition, 200ms
- Optional: Subtle scale (1.01), 200ms

**Hover Effects:**
- Background color transition, 200ms
- Shadow elevation increase, 200ms

**Click/Tap Feedback:**
- Scale down (0.95), 100ms
- Release: Scale up (1.0), 150ms

**Success/Error States:**
- Icon animation: Scale 0 → 1, bounce effect, 400ms
- Message slide-in: Slide from right, fade in, 300ms

### 5. Advanced Animations

**Gradient Animations:**
- Continuous gradient position shift, 5s ease infinite
- Blob pulse: Scale 1.0 → 1.05 → 1.0, 3s ease infinite

**Parallax Effects:**
- Subtle parallax on scroll (optional, performance permitting)
- Background elements move slower than foreground

---

## Integration Requirements

### 1. Backend API Integration

**Authentication:**
- JWT token management
- Token refresh mechanism
- OAuth callback handling

**Chat API:**
- WebSocket connection for real-time messages
- REST API fallback
- Message history retrieval
- Error handling and reconnection

**Endpoints:**
```
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh
GET  /api/chat/history
POST /api/chat/message
WebSocket: /ws/chat
```

### 2. Voice Integration

**Speech-to-Text (STT):**
- Google Speech Recognition API
- Vosk (offline fallback)
- Audio recording (Web Audio API / native APIs)
- Noise cancellation

**Text-to-Speech (TTS):**
- pyttsx3 (offline)
- gTTS (online)
- ElevenLabs (premium option)
- Voice customization (rate, volume, language)

### 3. Real-time Updates

**WebSocket:**
- Connection management
- Automatic reconnection
- Message queuing during disconnection
- Heartbeat/ping mechanism

**Push Notifications (Mobile):**
- iOS: APNs integration
- Android: FCM integration
- Notification permissions
- Badge updates

### 4. State Management

**Global State:**
- User authentication state
- Chat messages/conversations
- UI preferences (theme, language)
- Active mode

**Local State:**
- Form inputs
- UI component states (open/closed)
- Loading states
- Error states

**State Persistence:**
- JWT tokens: Secure storage (httpOnly cookies, Keychain/Keystore)
- User preferences: LocalStorage / AsyncStorage
- Chat history: Backend storage, local cache

---

## Performance Requirements

### 1. Load Time Targets

**Initial Load:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Total bundle size: < 500KB (gzipped)

**Subsequent Navigation:**
- Route transition: < 300ms
- Component render: < 100ms

### 2. Runtime Performance

**Frame Rate:**
- Target: 60 FPS
- Minimum: 30 FPS (acceptable for complex animations)

**Interaction Response:**
- Button click feedback: < 100ms
- Input typing: No lag
- Scroll: Smooth (60 FPS)

**Memory Usage:**
- Initial load: < 50MB
- Peak usage: < 200MB
- Memory leaks: None

### 3. Network Performance

**API Calls:**
- Request timeout: 30 seconds
- Retry logic: 3 attempts with exponential backoff
- Caching: Appropriate cache headers

**WebSocket:**
- Connection latency: < 500ms
- Message delivery: < 100ms (local network)

### 4. Optimization Strategies

**Code Splitting:**
- Route-based code splitting
- Lazy loading of heavy components
- Dynamic imports for non-critical features

**Asset Optimization:**
- Image optimization (WebP, compression)
- Icon fonts or SVG sprites
- Minification and compression (gzip/brotli)

**Rendering Optimization:**
- Virtual scrolling for long lists
- Debounce/throttle for frequent events
- Memoization for expensive computations
- React.memo for component optimization

---

## Testing Requirements

### 1. Visual Testing

**Design Consistency:**
- Design system compliance
- Component variations
- Responsive breakpoints
- Dark mode (if applicable)

**Cross-browser Testing:**
- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

**Platform Testing:**
- Web: Multiple browsers and devices
- Mobile: iOS and Android devices
- Desktop: Windows, macOS, Linux

### 2. Functional Testing

**User Flows:**
- Authentication (login, register, OAuth)
- Chat (send message, receive response)
- Voice input (record, transcribe, send)
- Settings (update preferences, save)

**Error Handling:**
- Network errors
- API errors
- Validation errors
- Permission errors

**Edge Cases:**
- Long messages
- Special characters
- Empty states
- Offline mode

### 3. Accessibility Testing

**Automated:**
- Lighthouse accessibility audit
- axe DevTools
- WAVE browser extension

**Manual:**
- Keyboard navigation
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Color contrast verification
- Focus management

### 4. Performance Testing

**Metrics:**
- Load time (Lighthouse, WebPageTest)
- Bundle size analysis
- Memory profiling
- CPU profiling

**Tools:**
- Lighthouse CI
- Chrome DevTools Performance
- React DevTools Profiler

### 5. Device Testing

**Physical Devices:**
- iOS: iPhone (various models), iPad
- Android: Various manufacturers and screen sizes
- Desktop: Windows PC, Mac, Linux machine

**Emulators/Simulators:**
- iOS Simulator
- Android Emulator
- Browser DevTools device emulation

---

## Implementation Checklist

### Design System
- [ ] Color palette defined and documented
- [ ] Typography scale implemented
- [ ] Spacing system in use
- [ ] Component library created
- [ ] Style guide documentation

### Web Application
- [ ] Landing page implemented
- [ ] Authentication pages (login, register)
- [ ] Chat interface complete
- [ ] Navigation implemented
- [ ] Responsive design verified
- [ ] Browser compatibility tested

### Mobile Application
- [ ] Landing screen implemented
- [ ] Authentication screens complete
- [ ] Chat screen with floating widget
- [ ] Navigation system
- [ ] iOS and Android tested
- [ ] App store assets prepared

### Desktop Application
- [ ] Main window with custom title bar
- [ ] Chat widget implemented
- [ ] System tray integration
- [ ] Platform-specific styling
- [ ] Build scripts for all platforms

### Integration
- [ ] Backend API connected
- [ ] WebSocket implementation
- [ ] Voice input/output working
- [ ] Authentication flow complete
- [ ] Error handling implemented

### Quality Assurance
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met
- [ ] Cross-platform testing complete
- [ ] User acceptance testing
- [ ] Documentation complete

---

## Appendices

### A. Design Tokens Reference

See `web-app/styles/globals.css` and design system documentation for complete token reference.

### B. Component Library

Component documentation available in:
- Web: `web-app/components/`
- Mobile: `mobile/src/components/`
- Desktop: `desktop/src/widgets/`

### C. API Documentation

Backend API documentation: `docs/api/`

### D. Figma Design Files

Design specifications: `chat UI.txt` (Figma export)

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2025 | Initial complete UI requirements document | System |

---

**End of Document**

