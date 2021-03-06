# TODO List

### Known Bugs
- `>repo` could use some improved fuzzy search cases (i.e. not freaking out over commas)

### Improvements
- Improve audience data storage (don't need text file)
- Improve README ([ROBOT_IS_YOU](https://github.com/RocketRace/robot-is-you) seems to be a good example)
- `>rule` command
- Add MegaCheer as query
 -Required documents check: should add '.txt' to settings.py
 - Migrate userlevels.txt and restrict/unrestrict/user permissions to .json

### New Features
- Roll random adventures from the book
- Shop/economy guidance
- Secret Nyx link command (>nyx) [wartorn: will add `>nyx` alias later]
- query and similar commands really should have some simple stuff like boolean joins.
- Chip or queries: simple+guard, support+guard
- Notion support

### Potential Ideas
- Add NaviChip creation rules
- Shop ideas for new GMs?
- General `repeat` command? (Element, Mysterydata, roll)
- Training GPT-2 on how to add a man with a gun to any scene

### Notes
* We may want to reconsider notion-py when it's built less like a walking security hole with its token requirements.
  I tried my best to figure out how the hell to run it in an anonymous session so that we didn't need to reconstruct
  the data structure by hand, but it fought me at every corner.
* My reasoning for this is that while the XHR structure might be the same now, there's no guarantee it will be later, especially when there's the looming idea of that private API beta going public.  There's already a recorded instance of this breaking in the past with unofficial APIs.
* And if there's any more evidence needed that Zone was right.. well, I found out just a few hours ago that the `token_v2` property could _break_ if you just decided to sign in and out to another account, entirely. That's not acceptable for our use case in any circumstance. -Wartorn