<div align="center">

# 🎬 vid2text

**Turn any video into text — in a few clicks, on your own computer.**

Pick a folder with videos, pick a folder for the results, press one button.<br>
No accounts, no uploads, no subscriptions.

<p>
  <a href="https://github.com/averageencoreenjoer/vid2text/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/averageencoreenjoer/vid2text/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT license">
</p>

<p>
  <img src="https://skillicons.dev/icons?i=python,fastapi,docker,githubactions,js,html,css&theme=dark" alt="Tech stack">
</p>

</div>

---

## 📖 Table of contents

- [What is this?](#-what-is-this)
- [What you get](#-what-you-get)
- [Quick start (easiest way, with Docker)](#-quick-start-easiest-way-with-docker)
- [Alternative: install without Docker](#-alternative-install-without-docker)
- [Using the app](#%EF%B8%8F-using-the-app)
- [Supported formats](#%EF%B8%8F-supported-formats)
- [What the results look like](#-what-the-results-look-like)
- [Choosing an accuracy level](#-choosing-an-accuracy-level)
- [Command line (optional)](#%EF%B8%8F-command-line-optional)
- [Frequently asked questions](#-frequently-asked-questions)
- [Troubleshooting](#%EF%B8%8F-troubleshooting)
- [For developers](#-for-developers)
- [License](#-license)

---

## 🤔 What is this?

**vid2text** listens to your videos and writes down what is said. It is handy for:

- 📝 meeting and lecture recordings,
- 🎓 online courses and webinars,
- 🎙️ interviews and podcasts,
- 🔎 making a huge video archive searchable.

Under the hood it uses [Whisper](https://github.com/openai/whisper), a well-known speech recognition model, through the fast [faster-whisper](https://github.com/SYSTRAN/faster-whisper) library. It understands about 100 languages and works **fully offline** once the model has been downloaded.

> 🔒 **Privacy:** your videos never leave your computer. Nothing is sent to any server.

## ✨ What you get

| | |
|---|---|
| 🖱️ **Simple interface** | A web page with three steps. No commands needed. |
| 📂 **Folder in → folder out** | Convert a whole folder (including sub-folders) at once. Results keep the same folder structure. |
| 🎞️ **Every common format** | MP4, MOV, MKV, AVI, WEBM, WMV, FLV and many more — even plain audio like MP3 and WAV. |
| 📄 **TXT and JSON** | Readable text for people, structured data for programs. Pick one or both. |
| 🌍 **Many languages** | Detects the language automatically, or you can choose it yourself. |
| ♻️ **Safe to re-run** | Already converted files are skipped, so you can stop and continue later. |
| 🐳 **Docker ready** | One command to run it anywhere, nothing else to install. |

---

## 🚀 Quick start (easiest way, with Docker)

Docker is a free program that runs apps in a ready-made box, so you don't need to install anything else.

### Step 1 — Install Docker

Download **Docker Desktop** for your system and install it like any other app:
👉 <https://www.docker.com/products/docker-desktop/>

Then open Docker Desktop and wait until it says it is running.

### Step 2 — Download vid2text

Click the green **Code** button at the top of this page → **Download ZIP**, then unzip it.<br>
(If you know Git: `git clone https://github.com/averageencoreenjoer/vid2text.git`)

### Step 3 — Start it

Open a terminal **inside the unzipped folder**:

- **Windows:** open the folder, click the address bar, type `cmd`, press Enter.
- **macOS:** right-click the folder → *New Terminal at Folder*.

Then run:

```bash
docker compose up --build
```

The first start takes a few minutes (it builds the app once). Later starts take seconds.

### Step 4 — Open the app

Open your browser and go to 👉 **<http://localhost:8000>**

### Step 5 — Add your videos

Two folders are created next to the project files:

| Folder | What it is for |
|---|---|
| `input/`  | Put your videos here |
| `output/` | Your text files will appear here |

Copy videos into `input/`, press **Start converting**, and collect the results from `output/`.

To stop the app, press `Ctrl + C` in the terminal.

> 💡 **Want to use videos from another place on your computer?** Open `docker-compose.yml` and replace `./input` with the full path of your folder, for example `C:/Users/Anna/Videos:/data/input` (Windows) or `/Users/anna/Movies:/data/input` (macOS).

---

## 🐍 Alternative: install without Docker

Prefer to run it directly? You need **Python 3.10 or newer** ([download](https://www.python.org/downloads/)).

```bash
git clone https://github.com/averageencoreenjoer/vid2text.git
cd vid2text

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install .
vid2text serve
```

Your browser opens automatically. ffmpeg (the tool that reads video files) is installed together with the app, so there is nothing else to set up.

---

## 🖥️ Using the app

The page has three numbered cards:

```
┌──────────────────────────────────────────────┐
│ ① Where are your videos?                     │
│   [ /Users/anna/Videos            ] [Browse…]│
├──────────────────────────────────────────────┤
│ ② Where should the text go?                  │
│   [ /Users/anna/Transcripts       ] [Browse…]│
│   Save as:  (✔ TXT)  (✔ JSON)                │
├──────────────────────────────────────────────┤
│ ③ Convert                                    │
│   [ Start converting ]                       │
│   ▓▓▓▓▓▓▓▓░░░░░░░░  3 of 8 files             │
└──────────────────────────────────────────────┘
```

1. **Choose the input folder.** Click **Browse…** and click through your folders, or paste the path. The app tells you how many video files it found.
2. **Choose the output folder** and tick the formats you want (TXT, JSON or both). The folder is created if it does not exist.
3. **Press *Start converting*.** A progress bar shows which file is being processed. You can press **Stop** at any time; finished files are kept.

When everything is done you will see a list with ✓ (done), ↷ (skipped) or ✕ (failed, with the reason).

### ⚙️ Advanced settings (optional)

Click *Advanced settings* to change:

- **Accuracy** — a bigger model is more accurate but slower. See [below](#-choosing-an-accuracy-level).
- **Spoken language** — leave on *Detect automatically* unless the results come out in the wrong language.
- **Include sub-folders** — on by default.
- **Add time marks to TXT files** — adds `[00:01:15]` at the start of every line.
- **Redo files that were already converted** — by default they are skipped.

The app remembers your folders and settings for next time.

> ⏳ **First run:** the speech model is downloaded once (from about 75 MB to 3 GB, depending on the accuracy you choose). After that it works offline. With Docker the model is stored in a Docker volume, so it is not downloaded again.

---

## 🎞️ Supported formats

**Video:** `mp4` `m4v` `mov` `mkv` `avi` `wmv` `flv` `f4v` `webm` `mpg` `mpeg` `m2v` `ts` `mts` `m2ts` `3gp` `3g2` `ogv` `vob` `asf` `rm` `rmvb` `divx` `mxf` `dv`

**Audio only:** `mp3` `wav` `m4a` `aac` `flac` `ogg` `opus` `wma` `amr`

If your video is in a rare format that is not listed, convert it to MP4 first, or open an issue.

---

## 📄 What the results look like

For a video called `lecture.mp4` you get `lecture.txt` and/or `lecture.json`.

**`lecture.txt`** — plain text, one phrase per line:

```text
Hello and welcome to today's lecture.
Let's start with a quick overview.
```

With *time marks* turned on:

```text
[00:00:00] Hello and welcome to today's lecture.
[00:00:04] Let's start with a quick overview.
```

**`lecture.json`** — structured data, useful if you want to process the text with other programs:

```json
{
  "source": "lecture.mp4",
  "language": "en",
  "duration": 312.4,
  "text": "Hello and welcome to today's lecture. Let's start with a quick overview.",
  "segments": [
    { "start": 0.0, "end": 3.2, "text": "Hello and welcome to today's lecture." },
    { "start": 3.2, "end": 6.8, "text": "Let's start with a quick overview." }
  ]
}
```

Videos in sub-folders produce results in the same sub-folders of the output directory.

---

## 🎯 Choosing an accuracy level

| Level | Download size* | Speed | Accuracy | Good for |
|---|---|---|---|---|
| `tiny` | ~75 MB | ⚡⚡⚡⚡⚡ | ★☆☆☆☆ | Quick tests, very clear speech |
| `base` | ~140 MB | ⚡⚡⚡⚡ | ★★☆☆☆ | **Default** — everyday use |
| `small` | ~460 MB | ⚡⚡⚡ | ★★★☆☆ | Good balance |
| `medium` | ~1.5 GB | ⚡⚡ | ★★★★☆ | Noisy audio, accents |
| `large-v3` | ~3 GB | ⚡ | ★★★★★ | Best quality, needs a strong computer |

\* Approximate. Not sure what to pick? Start with `base`; if the text has too many mistakes, try `small`.

---

## ⌨️ Command line (optional)

You don't need this if you use the web page. It is useful for automation.

```bash
# Convert a folder to both TXT and JSON
vid2text run ./videos ./transcripts

# Only TXT, Russian speech, better accuracy, with time marks
vid2text run ./videos ./transcripts -f txt -l ru -m small --timestamps

# Start the web interface on another port
vid2text serve --port 9000
```

| Option | Meaning |
|---|---|
| `-f`, `--format` | `txt` or `json` (repeat for both; default both) |
| `-m`, `--model` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `-l`, `--language` | Language code like `en`, `ru`, `de` (default: auto-detect) |
| `--timestamps` | Add time marks to TXT |
| `--no-recursive` | Ignore sub-folders |
| `--overwrite` | Redo files that already have results |

With Docker:

```bash
docker compose run --rm vid2text run /data/input /data/output -m small
```

---

## ❓ Frequently asked questions

**Is it free?** Yes, completely. It is open source under the MIT license.

**Do I need internet?** Only once, to download the speech model. After that it works offline.

**Does it need a powerful computer or a graphics card?** No. A normal laptop works; bigger models are just slower.

**Can it separate speakers ("Speaker 1 / Speaker 2")?** Not at the moment.

**Can it translate to another language?** Not at the moment; it writes down what is said, in the language that is spoken.

**What if a video has no sound?** That file is marked as failed with a clear reason, and the rest continue.

---

## 🛠️ Troubleshooting

| Problem | What to do |
|---|---|
| `docker: command not found` | Install Docker Desktop and make sure it is running. |
| The page does not open | Check that the terminal still shows the app running, then visit <http://localhost:8000>. If the port is busy, change `8000:8000` to `9000:8000` in `docker-compose.yml` and visit `localhost:9000`. |
| "No video or audio files were found" | Check that the videos are in the folder you chose and have a supported extension. |
| Stuck on "Preparing…" for a long time | The model is being downloaded on the first run. Wait, or choose a smaller accuracy level. |
| The text is in the wrong language | Open *Advanced settings* and choose the language manually. |
| The text has many mistakes | Pick a higher accuracy level (`small` or `medium`). |
| One file says "failed" | Read the reason shown next to it. The file may be damaged or have no audio track. |

---

## 👩‍💻 For developers

### Project layout

```
src/vid2text/
├── formats.py     supported file extensions
├── media.py       finding files, extracting audio with ffmpeg
├── engine.py      speech recognition (faster-whisper wrapper)
├── writers.py     TXT and JSON output
├── pipeline.py    the batch conversion logic
├── jobs.py        background job runner used by the web UI
├── cli.py         command line entry point
└── web/           FastAPI app and the static front-end
tests/             automated tests
```

### Run the tests

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

The tests replace the speech model with a tiny fake one, so they are fast and need no download. They still use real ffmpeg to build sample MP4, MKV, AVI, WEBM and MOV files.

### Continuous integration

Every push and pull request runs [GitHub Actions](.github/workflows/ci.yml):

- ✅ tests on Linux, macOS and Windows with Python 3.10 and 3.12,
- ✅ lint check with Ruff,
- ✅ Docker image build, the test suite inside the image, and a start-up check of the web interface.

### HTTP API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/config` | Models, supported extensions, default folders |
| `GET` | `/api/browse?path=…` | List sub-folders (used by the folder picker) |
| `POST` | `/api/jobs` | Start a conversion |
| `GET` | `/api/jobs/current` | Progress and results |
| `POST` | `/api/jobs/cancel` | Stop after the current file |

### Environment variables

| Variable | Meaning |
|---|---|
| `VID2TEXT_ROOTS` | Restrict the folder picker to these paths (used in Docker: `/data`) |
| `VID2TEXT_INPUT` / `VID2TEXT_OUTPUT` | Pre-filled folders in the interface |
| `VID2TEXT_MODEL_DIR` | Where downloaded models are stored |

> ⚠️ The web interface is meant for your own computer. It listens on `127.0.0.1` by default and has no login, so don't expose it to the internet.

---

## 📜 License

[MIT](LICENSE) © averageencoreenjoer
