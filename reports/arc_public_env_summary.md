# ARC-AGI-3 Public Environment Summary

Generated from `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files` on `2026-03-27T03:02:42Z`.

This report is static analysis over the organizer-provided public environment source files.
The notes are heuristic summaries, not executable proofs.

Total public environments: **25**

| Game | Title | Actions | Levels | Click Tags | Signals |
| --- | --- | --- | ---: | --- | --- |
| `ar25-e3c63847` | `AR25` | `[1, 2, 3, 4, 5, 6, 7]` | 8 | `[]` | `custom-valid-actions, display-overlay` |
| `bp35-0a0ad940` | `BP35` | `[]` | 9 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `cd82-fb555c5d` | `CD82` | `[1, 2, 3, 4, 5, 6]` | 6 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `cn04-65d47d14` | `CN04` | `[1, 2, 3, 4, 5, 6]` | 5 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `dc22-4c9bff3e` | `DC22` | `[1, 2, 3, 4, 6]` | 6 | `[]` | `hidden-state, display-overlay` |
| `ft09-0d8bbf25` | `FT09` | `[6]` | 6 | `['gOi']` | `hidden-state, color-remap, 3x3-pattern, custom-valid-actions, display-overlay` |
| `g50t-5849a774` | `G50T` | `[1, 2, 3, 4, 5]` | 7 | `[]` | `hidden-state` |
| `ka59-9f096b4a` | `KA59` | `[1, 2, 3, 4, 6]` | 7 | `[]` | `hidden-state, display-overlay` |
| `lf52-271a04aa` | `LF52` | `[]` | 10 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `lp85-305b61c3` | `LP85` | `[6]` | 8 | `[]` | `display-overlay` |
| `ls20-9607627b` | `LS20` | `[1, 2, 3, 4]` | 7 | `[]` | `hidden-state, color-remap, display-overlay` |
| `m0r0-dadda488` | `M0R0` | `[1, 2, 3, 4, 5, 6]` | 6 | `[]` | `hidden-state, color-remap, display-overlay` |
| `r11l-aa269680` | `R11L` | `[6]` | 6 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `re86-4e57566e` | `RE86` | `[1, 2, 3, 4, 5]` | 8 | `[]` | `hidden-state, display-overlay` |
| `s5i5-a48e4b1d` | `S5I5` | `[6]` | 8 | `['gdgcpukdrl', 'myzmclysbl']` | `hidden-state, custom-valid-actions, display-overlay` |
| `sb26-7fbdac44` | `SB26` | `[5, 6, 7]` | 8 | `['lngftsryyw', 'susublrply']` | `hidden-state, color-remap, custom-valid-actions, display-overlay` |
| `sc25-f9b21a2f` | `SC25` | `[1, 2, 3, 4, 6]` | 6 | `[]` | `hidden-state, 3x3-pattern, custom-valid-actions` |
| `sk48-41055498` | `SK48` | `[1, 2, 3, 4, 6, 7]` | 8 | `[]` | `hidden-state, color-remap, custom-valid-actions, display-overlay` |
| `sp80-0ee2d095` | `SP80` | `[1, 2, 3, 4, 5, 6]` | 6 | `[]` | `hidden-state, custom-valid-actions, display-overlay` |
| `su15-4c352900` | `SU15` | `[6, 7]` | 9 | `[]` | `custom-valid-actions, display-overlay` |
| `tn36-ab4f63cc` | `TN36` | `[6]` | 7 | `[]` | `` |
| `tr87-cd924810` | `TR87` | `[1, 2, 3, 4]` | 6 | `[]` | `hidden-state, color-remap, display-overlay` |
| `tu93-2b534c15` | `TU93` | `[1, 2, 3, 4]` | 9 | `[]` | `display-overlay` |
| `vc33-9851e02b` | `VC33` | `[]` | 7 | `['ACQ']` | `hidden-state, custom-valid-actions, display-overlay` |
| `wa30-ee6fef47` | `WA30` | `[1, 2, 3, 4, 5]` | 9 | `[]` | `hidden-state, display-overlay` |

## Per-game Notes

### `ar25-e3c63847`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/ar25/e3c63847/ar25.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[21, 21], [21, 21], [21, 21], [21, 21], [21, 21], [21, 21], [21, 21], [21, 21]]`
- Metadata baseline actions: `[17, 22, 103, 29, 29, 159, 152, 66]`
- Level data keys: `['StepCounter', 'edyhkfhkcf']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 5, 6, 7]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'khupblbrxc': 'edyhkfhkcf'}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `bp35-0a0ad940`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/bp35/0a0ad940/bp35.py`
- Levels: 9 with names `[]`
- Grid sizes: `[[8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8]]`
- Metadata baseline actions: `[15, 72, 36, 31, 31, 48, 86, 155, 163]`
- Level data keys: `[]`
- Action style: `unknown` with `available_actions=[]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `cd82-fb555c5d`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/cd82/fb555c5d/cd82.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[41, 8, 30, 21, 19, 17]`
- Level data keys: `[]`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 5, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `cn04-65d47d14`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/cn04/65d47d14/cn04.py`
- Levels: 5 with names `[]`
- Grid sizes: `[[20, 20], [20, 20], [20, 20], [20, 20], [20, 20]]`
- Metadata baseline actions: `[16, 54, 69, 318, 208, 114]`
- Level data keys: `['BackgroundColour']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 5, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `exlcvhdjsf` using custom win logic.

### `dc22-4c9bff3e`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/dc22/4c9bff3e/dc22.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[64, 44], [64, 48], [64, 48], [64, 48], [64, 64], [64, 64]]`
- Metadata baseline actions: `[64, 117, 59, 78, 324, 550]`
- Level data keys: `['StepCounter']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'pbkvtprbnmx': 'zgkdpiyghze', 'bqxa': 'bqxa', 'fdvakicpimr': 'pcxjvnmybet', 'wbzes': 'wbze', 'nxhz_list': 'nxhz'}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `uhqbwfdkff` using custom win logic.

### `ft09-0d8bbf25`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/ft09/0d8bbf25/ft09.py`
- Levels: 6 with names `['THR', 'hxv', 'Fmh', 'oea', 'INW', 'DFx']`
- Grid sizes: `[[32, 32], [32, 32], [32, 32], [32, 32], [32, 32], [32, 32]]`
- Metadata baseline actions: `[17, 19, 15, 21, 65, 26]`
- Level data keys: `['cwU', 'elp', 'kCv']`
- Action style: `click-only` with `available_actions=[6]`
- Clickable tags from `_get_valid_actions`: `['gOi']`
- Goal tags: `['bsT']`; win-check tags: `['Hkx', 'NTi']`
- Tag aliases from `on_set_level`: `{'gig': 'bsT', 'fhc': 'Hkx', 'mou': 'NTi'}`
- Click-only game: the agent acts through ACTION6 coordinates.
- Custom valid-action filtering is present; clickable sprites use tags ['gOi'].
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Step logic uses an explicit neighborhood/pattern mask, indicating local propagation effects.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `cgj` using template/goal sprites tagged ['bsT']; board checks against tags ['Hkx', 'NTi'].

### `g50t-5849a774`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/g50t/5849a774/g50t.py`
- Levels: 7 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[51, 175, 86, 52, 96, 48, 67]`
- Level data keys: `[]`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4, 5]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.

### `ka59-9f096b4a`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/ka59/9f096b4a/ka59.py`
- Levels: 7 with names `[]`
- Grid sizes: `[[45, 45], [63, 63], [54, 54], [54, 54], [63, 63], [63, 63], [63, 63]]`
- Metadata baseline actions: `[39, 175, 86, 47, 21, 132, 326]`
- Level data keys: `['StepCounter']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `cbdaoltbck` using custom win logic.

### `lf52-271a04aa`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/lf52/271a04aa/lf52.py`
- Levels: 10 with names `[]`
- Grid sizes: `[[8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8], [8, 8]]`
- Metadata baseline actions: `[24, 81, 74, 86, 118, 148, 189, 116, 150, 225]`
- Level data keys: `[]`
- Action style: `unknown` with `available_actions=[]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `lp85-305b61c3`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/lp85/305b61c3/lp85.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[32, 19], [41, 41], [39, 31], [57, 57], [27, 32], [60, 64], [48, 36], [63, 63]]`
- Metadata baseline actions: `[33, 22, 31, 23, 33, 34, 73, 173]`
- Level data keys: `['StepCounter', 'level_name']`
- Action style: `click-only` with `available_actions=[6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `['goal', 'goal-o']`
- Tag aliases from `on_set_level`: `{'afhycvvjg': 'sys_click'}`
- Click-only game: the agent acts through ACTION6 coordinates.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `khartslnwa` using board checks against tags ['goal', 'goal-o'].

### `ls20-9607627b`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/ls20/9607627b/ls20.py`
- Levels: 7 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[21, 123, 39, 92, 54, 108, 109]`
- Level data keys: `['Fog', 'GoalColor', 'GoalRotation', 'StartColor', 'StartRotation', 'StartShape', 'StepCounter', 'StepsDecrement', 'kvynsvxbpi']`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `['hoswmpiqkw', 'vjotnebuqo']`
- Tag aliases from `on_set_level`: `{'gudziatsk': 'sfqyzhzkij', 'htkmubhry': 'wgmbtyhvbc', 'htkmubhry_2': 'eqatonpohu', 'tsynhckng': 'ghizzeqtoh', 'srgbthxut': 'kvynsvxbpi', 'plrpelhym': 'rjlbuycveu'}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `pbznecvnfr` using board checks against tags ['hoswmpiqkw', 'vjotnebuqo'].

### `m0r0-dadda488`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/m0r0/dadda488/m0r0.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[11, 11], [13, 13], [13, 13], [11, 11], [15, 15], [13, 13]]`
- Metadata baseline actions: `[30, 209, 83, 86, 436, 126]`
- Level data keys: `['npwxa']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 5, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `r11l-aa269680`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/r11l/aa269680/r11l.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[7, 28, 30, 20, 37, 45]`
- Level data keys: `[]`
- Action style: `click-only` with `available_actions=[6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Click-only game: the agent acts through ACTION6 coordinates.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `re86-4e57566e`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/re86/4e57566e/re86.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[28, 38, 198, 57, 84, 117, 328, 221]`
- Level data keys: `['StepCounter']`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4, 5]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `cdjxpfqest` using custom win logic.

### `s5i5-a48e4b1d`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/s5i5/a48e4b1d/s5i5.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[19, 57, 85, 203, 82, 30, 76, 56]`
- Level data keys: `['Children', 'StepCounter']`
- Action style: `click-only` with `available_actions=[6]`
- Clickable tags from `_get_valid_actions`: `['gdgcpukdrl', 'myzmclysbl']`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Click-only game: the agent acts through ACTION6 coordinates.
- Custom valid-action filtering is present; clickable sprites use tags ['gdgcpukdrl', 'myzmclysbl'].
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `ulzimrggno` using custom win logic.

### `sb26-7fbdac44`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/sb26/7fbdac44/sb26.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[18, 16, 15, 15, 31, 24, 17, 17]`
- Level data keys: `[]`
- Action style: `hybrid` with `available_actions=[5, 6, 7]`
- Clickable tags from `_get_valid_actions`: `['lngftsryyw', 'susublrply']`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'qaagahahj': 'pkpgflvjel', 'dkouqqads': 'lngftsryyw', 'dewwplfix': 'susublrply'}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Custom valid-action filtering is present; clickable sprites use tags ['lngftsryyw', 'susublrply'].
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `sc25-f9b21a2f`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/sc25/f9b21a2f/sc25.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[39, 5, 32, 33, 66, 41]`
- Level data keys: `['ozhskarnd', 'sykpecmoq', 'wdsxxkugj']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Step logic uses an explicit neighborhood/pattern mask, indicating local propagation effects.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.

### `sk48-41055498`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/sk48/41055498/sk48.py`
- Levels: 8 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[15, 32, 35, 113, 304, 42, 63, 92]`
- Level data keys: `['grouped_pauses', 'lit_extension']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 6, 7]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'vbelzuaian': 'elmjchdqcn', 'lqwkgffeb': 'jtteddgeyl'}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `sp80-0ee2d095`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/sp80/0ee2d095/sp80.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[16, 16], [16, 16], [16, 16], [20, 20], [20, 20], [20, 20]]`
- Metadata baseline actions: `[11, 18, 17, 172, 102, 152]`
- Level data keys: `['rotation', 'steps']`
- Action style: `hybrid` with `available_actions=[1, 2, 3, 4, 5, 6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Hybrid action space: both button actions and coordinate clicks are available.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `su15-4c352900`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/su15/4c352900/su15.py`
- Levels: 9 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[18, 28, 50, 151, 18, 31, 50, 179, 41]`
- Level data keys: `['goal', 'steps']`
- Action style: `custom` with `available_actions=[6, 7]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'koprtgesg': 'key'}`
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `tn36-ab4f63cc`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/tn36/ab4f63cc/tn36.py`
- Levels: 7 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[23, 22, 26, 37, 25, 56, 61]`
- Level data keys: `['Positions', 'Programs', 'Reset', 'Rotations', 'Scales']`
- Action style: `click-only` with `available_actions=[6]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Click-only game: the agent acts through ACTION6 coordinates.

### `tr87-cd924810`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/tr87/cd924810/tr87.py`
- Levels: 6 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[37, 30, 39, 29, 63, 119]`
- Level data keys: `['alter_rules', 'double_translation', 'tree_translation']`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{'zdwrfusvmx': 'nxkictbbvzt'}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.

### `tu93-2b534c15`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/tu93/2b534c15/tu93.py`
- Levels: 9 with names `[]`
- Grid sizes: `[[39, 38], [45, 45], [45, 45], [51, 51], [49, 49], [45, 45], [45, 45], [42, 42], [51, 51]]`
- Metadata baseline actions: `[19, 15, 34, 42, 76, 91, 47, 23, 31]`
- Level data keys: `['StepCounter']`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `vpaafwwtxk` using custom win logic.

### `vc33-9851e02b`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/vc33/9851e02b/vc33.py`
- Levels: 7 with names `['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7']`
- Grid sizes: `[[32, 32], [32, 32], [52, 52], [64, 64], [64, 64], [64, 64], [48, 48]]`
- Metadata baseline actions: `[6, 13, 31, 59, 92, 24, 82]`
- Level data keys: `['RoA', 'TiD']`
- Action style: `unknown` with `available_actions=[]`
- Clickable tags from `_get_valid_actions`: `['ACQ']`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Custom valid-action filtering is present; clickable sprites use tags ['ACQ'].
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `gug` using custom win logic.

### `wa30-ee6fef47`
- Source: `/home/quan/pan2026_detector/arc-prize-2026-arc-agi-3/environment_files/wa30/ee6fef47/wa30.py`
- Levels: 9 with names `[]`
- Grid sizes: `[[64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64], [64, 64]]`
- Metadata baseline actions: `[125, 58, 259, 113, 499, 58, 186, 134, 132]`
- Level data keys: `['StepCounter']`
- Action style: `button-only` with `available_actions=[1, 2, 3, 4, 5]`
- Clickable tags from `_get_valid_actions`: `[]`
- Goal tags: `[]`; win-check tags: `[]`
- Tag aliases from `on_set_level`: `{}`
- Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.
- Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.
- Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.
- Winning is checked by `ymzfopzgbq` using custom win logic.
