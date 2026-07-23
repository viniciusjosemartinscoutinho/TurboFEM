<div align="center">

<img src="./assets/TurboFEM-Logo.png" alt="TurboFEM logo" width="140"/>

# TurboFEM

### The fast, open-source FEA desktop app that turns your mechanical model into results in under 30 seconds.

**TurboFEM helps you solve or validate your mechanical model in 30 seconds.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![CalculiX](https://img.shields.io/badge/Solver-CalculiX-orange?style=for-the-badge)](http://www.calculix.de/)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge)](#license)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#installation)

[Getting Started](#getting-started) •
[Why TurboFEM](#why-turbofem) •
[Demo](#demo) •
[Features](#features) •
[Roadmap](#roadmap) •
[Contributing](#contributing)

</div>

---

## Let's validate TurboFEM

<div align="center">

<video src="https://github.com/user-attachments/assets/1be1afce-c1ff-420e-a8b4-9860cf6bc621" controls width="800" poster="./assets/turbofem-preview.gif">
  Your browser does not support HTML5 video. <a href="./assets/turbofem-demo.mp4">Download the video here</a>.
</video>

*Watch the full step-by-step walkthrough (~2 min) — from "Let's Validate TurboFEM" to a validated 1D beam.*

<img src="./assets/example_beam_1D.jpg" alt="TurboFEM — 1D beam validation result" width="800"/>

*A 1D beam model, meshed, solved, and validated end-to-end inside TurboFEM.*

</div>

---

## Why TurboFEM

Most FEA tools force engineers to choose between **power** and **simplicity**. You either get a bare-metal solver with a brutal learning curve, or a "simple" tool that can't handle real engineering problems.

**TurboFEM is built to remove that trade-off.**

- ⚡ **Minutes, not weeks, to first result.** A clean, guided desktop interface takes you from geometry to validated results in under 30 seconds for standard linear cases — no scripting, no solver config files to hand-write.
- 🧠 **A learning curve built for engineers, not just FEA specialists.** The interface is designed so mechanical, aerospace, and civil engineers can be productive on day one — not after weeks of onboarding.
- 🌍 **Multi-language out of the box.** TurboFEM already ships with several languages built in, so teams anywhere can adopt it without an English-only barrier.
- 🎯 **Solid linear FEA accuracy**, powered by [CalculiX](http://www.calculix.de/), a proven, industry-used open-source solver (developed in Fortran and C/C++ ) — so speed doesn't come at the cost of trustworthy results.
- 🧩 **Open source and actively growing.** New capabilities are being added continuously — TurboFEM is evolving into a full toolkit, not a one-off script.
- 🚀 **Built for teams that need to move fast.** Startups and engineering teams get a shorter path from "we have a mechanical question" to "we have a validated answer" — which means faster iteration and real productivity gains, not just a nicer UI.

If your team validates mechanical models regularly and every extra hour of tooling friction costs you real engineering time, TurboFEM is built exactly for that problem.

---

## Features

| | |
|---|---|
| 🖥️ **Desktop GUI** | Full PySide6 interface — no terminal commands required to run a simulation |
| 🔩 **Solver integration** | Built on top of the solver ccx (developed in Fortran and C language) for validated linear mechanical analysis |
| 📐 **Geometry & sections** | Built-in tools to define cross-sections and geometric models |
| 🧱 **Materials database** | Ready-to-use material selection and configuration |
| 📊 **Result visualization** | Plot and inspect results directly inside the app |
| 🌐 **Multi-language interface** | Several languages included, switchable without reinstalling |
| 📦 **Standalone Windows build** | Packaged as a distributable `.exe` — no Python setup required for end users |
| 🔄 **Export to other FEA tools** | Export your mechanical model for use in tools like Abaqus |

---

## Getting Started

### Option 1 — Run the packaged app (recommended for most users)

1. Download `TurboFEM.exe` from the release link.
2. Install it in a path **without spaces** in the folder names.
3. Run `TurboFEM.exe`.
4. Load your mechanical model, run the analysis, and inspect or export your results.

### Option 2 — Run from source

```bash
# Requires Python already installed
python main_TurboFEM_versions.py
```

On first run (with an internet connection), TurboFEM automatically installs the Python packages it needs.

### Building the executable yourself

```bash
# From the TurboFEM_exe folder
python builder_of_TurboFEM_exe.py
```

> 💡 **Tip:** To reset TurboFEM to a different display language, delete the local `keys.txt` config file in `%LocalAppData%` and relaunch the app.

---

## Demo

The full walkthrough above validates a classic **1D beam** case end-to-end:

1. Define the geometry and cross-section
2. Assign material and boundary conditions
3. Run ccx, the fast solver (developed in Fortran and C++/C)
4. Inspect and validate the results — in well under 2 minutes

This is the same class of problem every mechanical engineer checks by hand before trusting a model — TurboFEM just gets you there fast enough to make that check part of your normal workflow, not a bottleneck.

---

## Tech Stack

- **Language:** Python
- **GUI:** PySide6
- **Solver:** ccx
- **Packaging:** PyInstaller
- **Localization:** custom translation engine, multiple languages included

---

## Roadmap

TurboFEM is under active development. Planned directions include:

- [ ] Expanded solver capabilities beyond linear analysis
- [ ] More material and section presets
- [ ] Broader export/import compatibility with other FEA suites
- [ ] Continued expansion of built-in languages

---

## Contributing

Contributions, issues, and feature requests are welcome. If you're an engineer who hits a wall using TurboFEM on a real model, that friction is exactly the kind of feedback that shapes the roadmap.

---

## License

TurboFEM is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See [`LICENSE`](./LICENSE) for the full text.

TurboFEM bundles and invokes [CalculiX](http://www.calculix.de/) as an external solver — It's a separate, independently licensed component (GPL-2.0-or-later) by Guido Dhondt and Klaus Wittig. Its license is included at `Solvers/S1/calculix/CalculiX-2.23.0-win-x64/bin/LICENSE.txt`.

---

<div align="center">

Built by engineers, for engineers who need answers — not a second job learning FEA tooling.

</div>
answers — not a second job learning FEA tooling.

</div>
=======
# Dev_TurboFEM
development of our TurboFEM
>>>>>>> 150015ff1e366d93d07c9bf957b2bf07185ebcd1
answers — not a second job learning FEA tooling.

</div>
=======
# Dev_TurboFEM
development of our TurboFEM
>>>>>>> 150015ff1e366d93d07c9bf957b2bf07185ebcd1
