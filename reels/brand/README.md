# Brand assets (not committed)

The engine expects `presenter.png`: your photo with the background removed (transparent PNG).
Make one from any clear, front-facing photo:

```bash
pip install "rembg[cpu]" pillow
python3 -c "from rembg import remove,new_session;from PIL import Image;im=remove(Image.open('photo.jpg'),session=new_session('u2net_human_seg'));im.crop(im.getbbox()).save('reels/brand/presenter.png')"
```

This folder is git-ignored so your face and voice sample are not published in this public repo.
For the scheduled daily routine (which starts from a fresh clone) either commit `presenter.png`
deliberately (`git add -f reels/brand/presenter.png`), or let the routine skip presenter scenes.
Never commit the raw voice sample: the cloned voice lives in Higgsfield and is referenced by id.
