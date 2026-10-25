# Getting started with BeatOctant (Dev build)

BeatOctant recommends what to play next in Beat Saber, based on your own play history. It uses a recommendation database (DB) built from BeatSaver maps, and all the recommendation work runs on your own PC.

[日本語](GettingStarted_ja.md)

> - **This is a Dev build (unstable).** Things may break. Not tested on Windows. See also [Known issues](#known-issues).
> - **Unofficial.** A fan-made mod and tools, not affiliated with Beat Games or Meta.
> - **The code is written mostly with AI (Anthropic's Claude).** The maintainer decides what to build and reviews every change. BeatOctant does not generate maps; it recommends existing maps from BeatSaver.
> - For problems and feedback, use the [BeatOctant Discord server](https://discord.gg/gx6k3nKZBe) (English or Japanese).

## Requirements

### System requirements

| Item | Requirement |
| --- | --- |
| OS | Windows 10 or 11 (uses WebView2; not tested) or Linux |
| Beat Saber | 1.40.8 (the version tested) |
| Memory | 2 GB or more free besides the game (OctantCompass loads the DB) |
| Disk | About twice the DB file's size free (the import unpacks it) |
| Linux: Beat Saber | Run through Steam's Proton |
| Linux: OctantCompass | WebKitGTK 4.1 and GTK 3 (`libwebkit2gtk-4.1-0` on Debian/Ubuntu, `webkit2gtk4.1` on Fedora, `webkit2gtk-4.1` on Arch). Tested on Ubuntu 24.04 |
| Linux: OctantPath Desktop | WebKitGTK 4.1 and libnotify (`libwebkit2gtk-4.1-0` and `libnotify4` on Debian/Ubuntu) |
| Linux: file picker | zenity or kdialog (without them, type the path) |

### Mods

| Mod | Version | |
| --- | --- | --- |
| BSIPA | 4.3.6 or later | Required |
| SiraUtil | 3.2.1 or later | Required |
| BeatSaberMarkupLanguage | 1.12.5 or later | Required |
| SongCore | 3.15.3 or later | Required |
| BeatSaberPlaylistsLib | 1.7.2 or later | Required |
| BeatSaverVoting | Tested with 2.4.6 | Optional. Upvotes and downvotes are used for recommendations and for keeping or deleting downloaded songs |

## What you get

| Part | What it does |
| --- | --- |
| [OctantPath](https://github.com/BeatOctant/OctantPath/releases) (`OctantPath.dll`) | The Beat Saber mod. Shows recommendations in game, downloads songs and rotates them |
| [OctantCompass](https://github.com/BeatOctant/OctantCompass/releases) | The recommendation server that runs outside the game. Reads the DB and answers OctantPath |
| [DB](https://github.com/BeatOctant/OctantCompass/releases) (`<version>.full.tar`) | The data used for recommending: numbers computed from audio and charts. It contains no audio or charts |
| [OctantPath Desktop](https://github.com/BeatOctant/OctantPath/releases) | See recommendations and pick songs on your PC without starting the game. Optional |

## Install

1. Put `OctantPath.dll` in the game folder's `Plugins`.
2. Start OctantCompass. On Linux, run the Linux build directly, not through Proton (it needs `chmod +x`; from a terminal, `./octantcompass-… gui`).
3. In OctantCompass's "Advanced" tab, under "Import from a file", pick the DB file (`.tar`) or type its path, and press "Import". You can delete the file afterwards.
4. When the mark at the top right of the window is a filled circle with "Ready", you are set. When unused (30 minutes by default) the DB is released and it shows a ring with "Resting"; it loads again on the next request, so you can keep using it. A diamond means stopped.
5. Pair (once, even on the same PC).
   1. In OctantCompass's "Status" tab, press "Pairing code" (6 digits, valid for 5 minutes).
   2. In Beat Saber, press "OctantPath" in the left menu, enter the code under "Connection to OctantCompass", and press "Pair". Leave the address empty if it is the same PC.
   3. "Connected" means you are linked.

Start OctantCompass before the game. "Start at login" in "Advanced" does this for you (not tested on Windows).

OctantPath Desktop pairs the same way from its "Settings" tab. Desktop is linked as a separate environment from the game.

## Using it

- **Mix**: pick a song in song select, press "Mix" and choose a type. A preview of a list starting from that song appears. Swap songs that don't fit with "⇔" or drop them with "✕", and add one more at a time with "Add a song" (up to 20). A downloaded song shows "▶", which selects it in song select (the preview opens again when you come back from playing). If it looks good, "Create" downloads them and opens the "OctantPath mix" playlist (replaced each time). Use "Save" to keep a list as its own playlist.
- **Recommendation panel**: the panel floating over song select lets you preview songs in the list and "Get" one to download and select it. With "Auto next" on, the next song in the list is selected when you come back from playing.
- **Your play history feeds the recommendations**: clears, fails, favorites and upvotes are used. With little history at first, recommendations are rough. More history is meant to give better fits, but this has not been well checked.
- **Desktop**: without starting the game, choose a starting song and a type to see recommendations, preview them, view charts in ArcViewer and make playlists.

### Downloaded songs (trials)

Songs OctantPath downloads are trials, kept in `UserData/OctantPath/Levels`, apart from your usual `CustomLevels`. Songs you get from the preview ("↓" or "Create") are trials too.

By default, at game start, favorited, upvoted and replayed songs move to `CustomLevels`, while downvoted songs, songs left unplayed for a while (15 days you launch the game, by default), and the oldest songs over the "Size limit for trial songs" are deleted. Songs in other playlists are never deleted. Only trials OctantPath downloaded are deleted; songs you installed yourself and your play records are never touched.

To keep everything, turn off "Delete trial maps automatically": OctantPath then neither deletes nor moves trials, and only writes what it would have done to the log. If `settings.json` cannot be read, or a limit is set to 0 or below, nothing is deleted.

## Network

### Sent to external services

Nothing. Your play history (including accuracy) is not sent to any external service. BeatOctant does not submit scores either. If you have the ScoreSaber or BeatLeader mod, it submits as usual when you play a recommended song. OctantPath neither stops nor changes that.

### Traffic for getting songs

- **BeatSaver**: song info, covers, previews and map zips, only for songs you pick or that show up in recommendations. Requests are spaced out to keep the load on BeatSaver low.
- **GitHub**: on first use, OctantPath Desktop downloads ArcViewer (GPLv3, about 80 MB) for chart previews, one pinned version.

### Between OctantPath and OctantCompass

Your play history is handed to the OctantCompass you paired, so recommendations can be computed locally. On the same PC it stays on `127.0.0.1`. If you pair with OctantCompass on another PC, the history goes to that PC over your LAN. OctantCompass only answers the OctantPath you paired. The only time it connects out itself is "Import from the index", which the Dev build does not use.

### DB license

CC BY-NC-SA 4.0 (non-commercial, share alike). The terms and credits are inside the DB and can be read in the DB section of OctantCompass's "Advanced" tab.

## Known issues

- **Not tested on Windows.** The Windows builds of OctantCompass and OctantPath Desktop are built but have never been run; everything has only been tried on Linux (Proton). Please tell us how it goes on Windows.
- **Recommendation quality is not well checked yet.** The maintainer hurt a wrist and the right elbow, so there has been little long-session play testing. Please tell us how the recommendations feel: good fits, bad fits, too many, too few.
- **There are a lot of recommendation types.** They will be trimmed once it is clear which ones people use.
- **Adding or removing songs while the game is running has not been fully checked against the game.** The in-game UI can only take certain shapes, too.
- **Updates may break things.** Keep every part and the DB on their latest versions. An update may ask you to import the DB again or pair again. OctantPath never silently deletes your play history (`UserData/OctantPath`); if a version needs it rebuilt, its release notes will say so first.
- **The Quest version (OctantPathAndroid) is not covered.** It is very early, and there are no prebuilt releases.

## Troubleshooting

| Message | What to check |
| --- | --- |
| "Cannot reach OctantCompass" | Is OctantCompass running (does its window open)? Start it before the game |
| "Pairing needed" / "Pairing was refused" | Get a new code in the OctantCompass window and enter it (expires in 5 minutes, or after 5 wrong tries) |
| "Getting ready" | OctantCompass is loading the DB. Wait a moment |
| "Recommendations are unavailable" | Look at the reason in OctantCompass's "Status" tab. Import the DB file again |
| "…don't match" (version) | Update both OctantPath and OctantCompass to their latest versions |
| Few or no recommendations | The starting song may not be in the DB. Try another song |

When reporting in `#bug-reports` on the [BeatOctant Discord server](https://discord.gg/gx6k3nKZBe), please include the items below. Logs contain folder paths (which may include your user name) and the names of songs you played. Check that there is nothing you don't want to share before sending.

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

The specs and design documents (the [OctantSpecs README](README.md) and everything it links to) are in Japanese. This guide is the only English document.
