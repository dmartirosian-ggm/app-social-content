# Spark

Spark: Chore & Reward Chart, a chore and reward chart for parents of kids 2 to 6.
Colors, fonts and icons are copied from the app's own code, so posts look like the app.

- `clip.py`: "tiny habit of the day", 7 seconds, 1080x1920, 30 fps. A habit pops in, a week
  of stars fills, confetti, then an end card. One JSON file per clip in `clips/`.
- `pin.py`: routine chart pin, 1000x1500 PNG. `kind` is `morning` (yellow) or `bedtime`
  (purple). Use `\n` in the title to choose where it breaks. One JSON file per pin in `pins/`.
- `captions.md`: captions and hashtags for the first week of clips, and pin titles and text.

Icons you can use (the app's habit icons): tooth, shirt, bowl, toys, hands, book, potty,
sleep, shoes, bath, water, vegetables, backpack, kind, star. The background color follows
the icon, the same way the app tints habit tiles.

```
python apps/spark/clip.py
python apps/spark/pin.py
```
