# 🌿 GreenBuddy AI

**An open-weight AI gardening companion that helps people spend less time on screens and more time outdoors.**

GreenBuddy AI combines local AI with practical gardening activities. It helps users identify plants from photos, explore plant-care advice, generate seasonal planting plans, and complete outdoor missions.

## ✨ Features

- **Plant identification:** Classify plant photos using an image-classification model.
- **AI gardening assistant:** Ask gardening questions using a local Qwen model through Ollama.
- **Plant-care guidance:** Get beginner-friendly care suggestions for identified plants.
- **Planting planner:** Generate gardening suggestions based on location, growing space, and season.
- **Outdoor missions:** Choose simple activities that encourage time in nature.
- **Local processing:** Run AI inference on your computer after downloading the required models.

## 🧰 Technology Stack

- Python
- Flask
- HTML, CSS, and JavaScript
- Ollama
- Qwen 2.5 3B
- Hugging Face Transformers
- PyTorch
- Pillow

## 🚀 Installation on Windows

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd GreenBuddyAI
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install Ollama

Download Ollama from https://ollama.com/download/windows.

Download the language model:

```bash
ollama pull qwen2.5:3b
```

### 5. Start GreenBuddy AI

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## 🪴 How to Use

1. Open the local website.
2. Upload a plant photo and review the predictions.
3. Ask GreenBuddy gardening questions.
4. Generate a planting plan for your region and growing space.
5. Choose an outdoor mission and complete it in the real world.

## 🔒 Privacy and Offline Use

The application sends language-model requests to the local Ollama service and runs plant-image classification locally after the required model has been downloaded.

Initial installation and model downloads require internet access. Some features may need additional network access if their model files are not cached.

## ⚠️ Limitations

AI-generated plant identifications and gardening advice may be incorrect. Verify species, plant toxicity, and important care recommendations before acting on them.

The planting planner currently generates general guidance; it does not retrieve live weather or verify an official regional planting calendar.

## 📸 Screenshots and Demo

Add screenshots of the working application and a demonstration video or link here.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

## 📄 License

Choose a license after checking the licenses of the code, model weights, and dependencies used in this project.

---

Built with open-weight AI to help people connect with nature. 🌱