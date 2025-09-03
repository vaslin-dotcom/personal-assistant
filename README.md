# 🤖 Jarvis - Your Personal AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/LiveKit-Agents-orange?logo=webrtc" />
  <img src="https://img.shields.io/badge/Status-Active-success" />
  <img src="https://img.shields.io/github/license/vaslin-dotcom/personal-assistant" />
</p>

---

## ✨ Overview

**Jarvis** is a smart personal assistant built in Python that can perform everyday tasks using **voice**.
It combines **AI, LiveKit Agents, reminders, file management, and media control** into one simple interface.

Think of it as your own **Iron Man–style assistant** ⚡

---

## 🚀 Features

✅ Voice & Text interaction (toggle between console & audio modes)
✅ Search the web 🌍
✅ File management (open,play,pause,volume controll) 📂
✅ Smart reminders ⏰
✅ Play YouTube songs 🎵
✅ Extensible design → add your own tools easily

---

## 🛠️ Tech Stack

* **Python 3.10+**
* [LiveKit Agents](https://github.com/livekit/agents) – Realtime AI framework
* `dotenv` – Manage environment variables
* `requests` – API calls
* `sounddevice` / `PortAudio` – Audio input-output
* Custom tools:

  * **File Manager**
  * **Remainders**
  * **YouTube Player**
  * **Web Research**

---

## 📂 Project Structure

```
personal-assistant/
│── agent.py            # Main entrypoint
│── prompts.py          # Prompt templates
│── remainders.py       # Reminder module
│── file_manager.py     # File handling module
│── browse.py           # Web & YouTube integration
│── research.py         # Research assistant
│── requirements.txt    # Dependencies
└── README.md           # Project docs
```

---

## ⚡ Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/<your-username>/personal-assistant
   cd personal-assistant
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

### Run in Console Mode 

```bash
python agent.py console
```






## 🔮 Roadmap

* [ ] Add natural language file search
* [ ] Integrate calendar scheduling
* [ ] Add more media commands
* [ ] Cloud deployment option

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo 🍴
2. Create your feature branch
3. Commit your changes with clear messages
4. Open a PR 🚀



---

<p align="center">⭐ If you like this project, give it a star on GitHub!</p>
