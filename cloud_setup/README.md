# Avatar Generation Setup

## Overview
This folder contains tools to generate a photorealistic AI human avatar for Jarvis X V2.

## Quick Start

### Option 1: Use Colab Notebook (Recommended)
1. Open `colab_avatar_setup.ipynb` in Google Colab
2. Run all cells (takes ~15-20 minutes)
3. Download generated assets (ZIP file)
4. Unzip to `assets/avatar/base_videos/`

### Option 2: Use Pre-made Avatar (Alternative)
If you prefer to skip generation:
1. Run `python download_assets.py --preset professional`
2. This downloads a pre-generated avatar from free sources
3. Assets saved to `assets/avatar/base_videos/`

## Generated Assets

After completion, you'll have:
```
assets/avatar/base_videos/
├── face_reference.png      # Static portrait (512x512)
├── base_neutral.mp4        # Neutral talking (5 sec loop)
├── base_happy.mp4          # Happy expression (5 sec loop)
└── base_serious.mp4        # Serious expression (5 sec loop)
```

## Cost
- **$0** - Completely free using Google Colab GPU

## Next Steps
After avatar generation:
1. Verify files in `assets/avatar/base_videos/`
2. Proceed to Phase 2: Voice I/O System
3. Run `python avatar_interface.py` to test

## Troubleshooting

**Q: Colab session times out**
A: Re-run from the cell that failed. Progress is saved.

**Q: Download fails**
A: Use Option 2 (pre-made avatar) or retry download.

**Q: Video quality issues**
A: Regenerate with higher resolution in Colab settings.

**Q: Need different face**
A: Edit the prompt in Colab cell #2 and regenerate.

## Technical Details

**Avatar Generation:**
- Face: Stable Diffusion 1.5
- Animation: SadTalker
- Resolution: 512x512 (scales to 640x480 for display)
- Format: MP4 (H.264)

**System Requirements (Colab):**
- GPU: T4 or better (free tier)
- RAM: 12GB (provided by Colab)
- Storage: ~500MB for outputs

**System Requirements (Local):**
- None for generation (runs on Colab)
- ~50MB storage for downloaded assets

