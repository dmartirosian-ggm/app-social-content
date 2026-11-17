# App social content

Short videos and Pinterest pins for GBY Media's apps, made from small text files.
Each app gets its own folder with its colors, fonts, icons and post ideas. The code that
turns those into finished files is shared, so a new app only needs its own look and its
own layouts.

```
engine/          shared code: text, animation, confetti, sound, saving PNG/JPG/MP4
apps/spark/      Spark: Chore & Reward Chart
  brand.py         colors, fonts, icons, and shapes like stars and cards
  clip.py          the 7-second "tiny habit of the day" video
  pin.py           the weekly routine chart pin
  clips/*.json     one file per video
  pins/*.json      one file per pin
  captions.md      captions, hashtags and pin text for the first week
  fonts/           the app's fonts
out/             finished files land here (not saved in git)
```

## Setup (once)

You need Python 3 and ffmpeg. Then:

```
pip install -r requirements.txt
```

Install each app's fonts on the computer (for Spark, the six files in `apps/spark/fonts/`;
on Windows select them, right-click, Install). CairoSVG also needs the Cairo library: on a
Mac run `brew install cairo`, on Windows install the GTK3 runtime or use WSL.

## Make the files

Run these from the top folder of the repo.

```
python apps/spark/clip.py                                  # every Spark video
python apps/spark/pin.py                                   # every Spark pin
python apps/spark/clip.py apps/spark/clips/01-brush-teeth.json   # just one
```

Videos go to `out/spark/clips/` (an MP4 plus a cover JPG), pins to `out/spark/pins/`.
Add `--out some/folder` to put them somewhere else. The same file always gives the same
video, so nothing needs to be kept once it's posted.

To make a new post, copy one of the JSON files, change the words, and run the command
again. The fields each file takes are listed at the top of that app's `clip.py` and `pin.py`.

## Add the next app

1. Copy `apps/spark/` to a new folder named after the app, for example `apps/ayah-daily/`.
2. Delete the copied `clips/`, `pins/` and `captions.md` contents, and put the new app's
   fonts in `fonts/`.
3. In `brand.py`, change the app name, tagline, colors, icons and the font list to match
   the new app. The shapes at the bottom (stars, cards, pills) can be changed or replaced
   to fit its style.
4. Change the layouts in `clip.py` and `pin.py`, or replace them with the new app's own
   formats (a verse card, a level preview, a park photo card). Keep the last few lines
   that read the JSON files and save the output, since that part is the same for every app.
5. Add a few JSON files and run `python apps/<app>/clip.py` to check the result.

Anything two apps end up needing the same way belongs in `engine/`, so it's written once.

## Notes

- The sound in each video is made in code (a soft chord and little plucks), so there's
  nothing to license.
- This repo only makes the files. Posting and scheduling happen in Postiz.
