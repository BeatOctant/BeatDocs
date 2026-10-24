# Getting started with BeatOctant (Dev build)

BeatOctant recommends what to play next in Beat Saber, based on your own play history. It uses a recommendation database (DB) built from BeatSaver maps, and all the recommendation work runs on your own PC.

[日本語](GettingStarted_ja.md)

## Known issues

This is a Dev build (unstable) that anyone can download. Here are the weak spots we already know about.

- **Not tested on Windows.** The maintainer has no Windows PC. The Windows builds of OctantCompass and OctantPath Desktop are built but have never been run; everything has only been tried on Linux (Proton). Reports of whether it works on Windows are very welcome.
- **Recommendation quality is not well checked yet.** The maintainer swung a little too hard in Beat Saber and hurt a wrist and the right elbow. So: a tool that tells you what to play next, built by someone who can't play right now. There has been little long-session play testing. Please tell us how the recommendations feel: good fits, bad fits, too many, too few.
- **There are a lot of recommendation types.** The type list is long. It will be trimmed once it is clear which ones people use.
- **Some technical parts are still rough.** The in-game UI can only take certain shapes, and adding or removing songs while the game is running has not been fully checked against the game. The DB uses about 2 GB of memory while loaded.
- **Updates may break things.** Keep OctantPath, OctantCompass, OctantPath Desktop and the DB all on their latest versions. An update may ask you to import the DB again or pair again. OctantPath never silently deletes your play history (`UserData/OctantPath`); if a version needs it rebuilt, its release notes will say so first.

If something goes wrong or you notice anything, please let us know on the [BeatOctant Discord server](https://discord.gg/gx6k3nKZBe): bugs in `#bug-reports`, recommendation hits and misses and ideas in `#feedback-ideas`. English or Japanese is fine (Japanese chat is in `#日本語`).

The specs and design documents (the [OctantSpecs README](README.md) and everything it links to) are in Japanese. This guide is the only English document.

BeatOctant is written mostly with AI coding agents (Anthropic's Claude). The maintainer decides what to build and reviews every change. It does not generate maps; it recommends existing maps from BeatSaver.

## What you get

There are Windows and Linux builds. File names include the version and the OS. OctantPath and OctantPath Desktop are on [OctantPath's Releases](https://github.com/BeatOctant/OctantPath/releases), and OctantCompass and the DB are on [OctantCompass's Releases](https://github.com/BeatOctant/OctantCompass/releases).

| Part | File | What it does |
| --- | --- | --- |
| OctantPath | `OctantPath.dll` | The Beat Saber mod. Shows recommendations in game, downloads songs and rotates them. Same file for Windows and Linux |
| OctantCompass | `octantcompass-…` (`.exe` on Windows) | The recommendation server that runs outside the game. Reads the DB and answers OctantPath |
| DB | `<version>.full.tar` (one file) | The data used for recommending: numbers computed from audio and charts. It contains no audio or charts |
| OctantPath Desktop | `OctantPath.Desktop-…` (`.exe` on Windows) | See recommendations and pick songs on your PC without starting the game. Optional |

The Quest version (OctantPathAndroid) is not covered here. It is very early and unstable, and there are no prebuilt releases yet.

## What goes outside your PC

- **From BeatSaver**: song info, covers, previews and map zips, only for songs you pick or that show up in recommendations. Requests are spaced out to keep the load on BeatSaver low.
- **Desktop, on first use**: ArcViewer (GPLv3, about 80 MB) for chart previews, one pinned version from GitHub.
- **Your play history**: is not sent anywhere. It (including accuracy) is only handed to the OctantCompass you paired, so recommendations can be computed locally.
- **Scores**: BeatOctant does not submit scores. If you have the ScoreSaber or BeatLeader mod, it submits as usual when you play a recommended song. OctantPath neither stops nor changes that.
- **DB license**: CC BY-NC-SA 4.0 (non-commercial, share alike). The terms and credits are inside the DB and can be read in the DB section of OctantCompass's "Advanced" tab.

## Install

### 1. OctantPath (mod)

1. Use Beat Saber **1.40.8**. OctantPath works only on this version.
2. Install these mods, for example with BSManager (ModAssistant also works on Windows):
   - BSIPA (4.3.6 or later)
   - SiraUtil (3.2.1 or later)
   - BeatSaberMarkupLanguage (1.12.5 or later)
   - SongCore (3.15.3 or later)
   - BeatSaberPlaylistsLib (1.7.2 or later)
3. Put `OctantPath.dll` in the game folder's `Plugins`.

On Linux, run Beat Saber through Steam's Proton. Mods install the same way as on Windows; the game folder is in your Steam library (usually `~/.local/share/Steam/steamapps/common/Beat Saber`).

### 2. OctantCompass and the DB

1. Put the OctantCompass executable in any folder and double-click it. The OctantCompass window opens.
2. In the "Advanced" tab, under "Import from a file", pick the DB file (`.tar`) with "Choose…" or type its path, then press "Import". If "Choose…" opens nothing, type the path. OctantCompass checks the DB and unpacks it into its own data folder, so the disk holding that data folder needs about twice the file's size free. You can delete the file afterwards.
3. When the "Status" tab shows "Ready", you are set. The DB uses about 2 GB of memory while loaded. When unused (30 minutes by default) it is released and shows "Resting"; it loads again when OctantPath asks.

Start OctantCompass before starting the game. To skip that each time, turn on "Start at login" in "Advanced" (not yet tested on Windows). If it is still not running after login, start it yourself.

OctantCompass only answers the OctantPath you paired. The only time OctantCompass itself connects out is "Import from the index", which the Dev build does not use.

On Linux, run the Linux builds of OctantCompass and OctantPath Desktop directly, not through Proton. Make them executable first (`chmod +x octantcompass-… OctantPath.Desktop-…`). To start OctantCompass from a terminal, add `gui` (`./octantcompass-… gui`). "Choose…" needs zenity or kdialog.

## Pairing (once)

OctantPath and OctantCompass are linked once with a code, even on the same PC.

1. In OctantCompass's "Status" tab, press "Pairing code" (6 digits, valid for 5 minutes).
2. Start Beat Saber and press "OctantPath" in the left menu.
3. Under "Connection to OctantCompass", enter the code and press "Pair". Leave the address empty if it is the same PC.
4. "Connected" means you are linked.

OctantPath Desktop pairs the same way from its "Settings" tab. Desktop is linked as a separate environment from the game.

## Using it

- **Mix**: pick a song in song select, press "Mix" and choose a type. A preview of a list starting from that song appears. Swap songs that don't fit with "⇔" or drop them with "✕", and add one more at a time with "Add a song" (up to 20). A downloaded song shows "▶", which selects it in song select (the preview opens again when you come back from playing). If it looks good, "Create" downloads them and opens the "OctantPath mix" playlist (replaced each time). Use "Save" to keep a list as its own playlist.
- **Recommendation panel**: the panel floating over song select lets you preview songs in the list and "Get" one to download and select it. With "Auto next" on, the next song in the list is selected when you come back from playing.
- **It fits better the more you play**: clears, fails, favorites and upvotes all count. With little history at first, recommendations are rough.
- **Downloaded songs**: songs OctantPath downloads are trials, kept in `UserData/OctantPath/Levels`, apart from your usual `CustomLevels`. Songs you get from the preview ("↓" or "Create") are trials too. By default, at game start, favorited, upvoted and replayed songs move to `CustomLevels`, while downvoted songs, songs left unplayed for a while (15 days you launch the game, by default), and the oldest songs over the "Size limit for trial songs" are deleted. Songs in other playlists are never deleted. Only trials OctantPath downloaded are deleted; songs you installed yourself and your play records are never touched. To keep everything, turn off "Delete trial maps automatically": OctantPath then neither deletes nor moves trials, and only writes what it would have done to the log. If `settings.json` cannot be read, or a limit is set to 0 or below, nothing is deleted.
- **Desktop**: without starting the game, choose a starting song and a type to see recommendations, preview them, view charts in ArcViewer and make playlists.

## Troubleshooting

| Message | What to check |
| --- | --- |
| "Cannot reach OctantCompass" | Is OctantCompass running (does its window open)? Start it before the game |
| "Pairing needed" / "Pairing was refused" | Get a new code in the OctantCompass window and enter it (expires in 5 minutes, or after 5 wrong tries) |
| "Getting ready" | OctantCompass is loading the DB. Wait a moment |
| "Recommendations are unavailable" | Look at the reason in OctantCompass's "Status" tab. Import the DB file again |
| "…don't match" (version) | Update both OctantPath and OctantCompass to their latest versions |
| Few or no recommendations | The starting song may not be in the DB. Try another song |

When reporting in `#bug-reports` on the [BeatOctant Discord server](https://discord.gg/gx6k3nKZBe), please include:

- What you did and what happened (screenshots help)
- `Logs/_latest.log` in the game folder. OctantPath's lines are tagged `OctantPath` inside the game's log. Earlier runs are kept in the same folder as dated `.log.gz` files
- OctantCompass's "Status" tab and log (copy them from the window)
- For feedback on recommendations, the file written by "Write recommendation summary" in OctantPath's settings (`UserData/OctantPath/summaries/`). It holds per-type counts and recent recommendations, which is part of your play history. Sending it is up to you

## Uninstall

- **OctantPath**: delete `Plugins/OctantPath.dll`. To remove its records too, delete `UserData/OctantPath` and `Playlists/OctantPath`. Songs OctantPath downloaded are in `UserData/OctantPath/Levels`.
- **OctantCompass**: if "Start at login" is on, turn it off in the window first. Press "Stop", then delete the executable. Its data is in `%LOCALAPPDATA%\OctantCompass` on Windows, and `~/.config/OctantCompass`, `~/.local/state/OctantCompass` and `~/.local/share/OctantCompass` on Linux.
- **OctantPath Desktop**: delete the executable. Its data is in `%LOCALAPPDATA%\OctantPath\Desktop` on Windows, and `~/.config/OctantPath/Desktop`, `~/.local/state/OctantPath/Desktop`, `~/.local/share/OctantPath/Desktop` and `~/.cache/OctantPath/Desktop` on Linux. Desktop's "Settings" tab shows the folders in use.
- **DB**: lives in OctantCompass's data (`dbs` in the folders above) and goes away with it.

OctantPath only reads the game's other files (PlayerData, favorites, votes, scores, replays); it never changes them.
