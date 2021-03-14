# TODO List

### Known Bugs
- bugreport does not work in private messages
- query and similar commands really should have some simple stuff like boolean joins.
- Tinker & Reroute are not blue
  * [wartorn] i fixed this manually, but it's a problem that originates from the master autofill and thus the same sheets we use to feed progbot with data.
  * it's a case sensitivity issue with `Hotswap` where tinker and reroute depend on `HotSwap` as the parent of the color key, but that doesn't exist. maybe prod riject to fix that?
  * in the mean time, i'll look into tightening the case sensitivity in the color key later.
- BlackBlossom's art is in TaskManager

### Improvements
- Improve audience data storage (don't need text file)
- Improve README ([ROBOT_IS_YOU](https://github.com/RocketRace/robot-is-you) seems to be a good example)
- Alphabetical ordering for `>commands`!
- `>rule` command
- Add MegaCheer as query
- Exclude MegaVirus powers
- query and similar commands really should have some simple stuff like boolean joins.
- Chip or queries: simple+guard, support+guard
- Unknown command error?

### New Features
- Roll random adventures from the book
- Shop/economy guidance
- Secret Nyx link command (>nyx, >rulebook nyx) [wartorn: will add `>nyx` alias later]
- `>npu 3EB`

### Potential Ideas
- Add NaviChip creation rules
- Shop ideas for new GMs?
- Improve `>commands` to be pretty
- General `repeat` command? (Element, Mysterydata, roll)
