const form = document.getElementById("question-form");
const questionInput = document.getElementById("question");
const answerBox = document.getElementById("answer");
const askButton = document.getElementById("ask-button");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();
    if (!question) return;

    askButton.disabled = true;
    askButton.textContent = "Thinking...";
    answerBox.textContent = "Growing an answer for you... 🌱";

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        // textContent safely displays the model response as text.
        answerBox.textContent = data.answer;
    } catch (error) {
        answerBox.textContent = error.message;
    } finally {
        askButton.disabled = false;
        askButton.textContent = "Ask GreenBuddy";
    }
});


const missionCheckboxes = document.querySelectorAll(".mission input");
const progress = document.getElementById("progress");

const STORAGE_KEY = "greenbuddy-completed-missions";

function loadMissions() {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");

        missionCheckboxes.forEach((checkbox, index) => {
            checkbox.checked = saved.includes(index);
        });
    } catch {
        // If saved data is invalid, start with unchecked missions.
        missionCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    updateProgress();
}

function updateProgress() {
    const completed = [];

    missionCheckboxes.forEach((checkbox, index) => {
        if (checkbox.checked) {
            completed.push(index);
        }
    });

    progress.textContent =
        `${completed.length} of ${missionCheckboxes.length} missions completed 🌱`;

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(completed));
    } catch {
        // The checklist still works if browser storage is unavailable.
    }
}

missionCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", updateProgress);
});

loadMissions();


const plantForm = document.getElementById("plant-form");
const plantPhoto = document.getElementById("plant-photo");
const plantResult = document.getElementById("plant-result");
const identifyButton = document.getElementById("identify-button");

plantForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = plantPhoto.files[0];

    if (!file) {
        plantResult.textContent = "Please choose a plant photo.";
        return;
    }

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        plantResult.textContent = "Please choose a JPG, PNG, or WebP image.";
        return;
    }

    if (file.size > 8 * 1024 * 1024) {
        plantResult.textContent = "Please choose an image smaller than 8 MB.";
        return;
    }

    const formData = new FormData();
    formData.append("photo", file);

    identifyButton.disabled = true;
    identifyButton.textContent = "Analyzing photo...";
    plantResult.textContent =
        "Loading the local plant-recognition model. The first run may take a while.";

    try {
        const response = await fetch("/api/identify", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Plant identification failed.");
        }

        plantResult.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent = "Top plant predictions";
        plantResult.appendChild(heading);

        data.predictions.forEach((plant, index) => {
            const item = document.createElement("p");
            item.textContent =
                `${index + 1}. ${plant.name} — ${plant.confidence}% model score`;
            plantResult.appendChild(item);
        });

        const notice = document.createElement("p");
        notice.textContent = data.notice;
        plantResult.appendChild(notice);

    } catch (error) {
        plantResult.textContent = error.message;
    } finally {
        identifyButton.disabled = false;
        identifyButton.textContent = "Identify my plant";
    }
});


const careButton = document.getElementById("care-button");
const careResult = document.getElementById("care-result");

careButton.addEventListener("click", async () => {
    const file = plantPhoto.files[0];

    if (!file) {
        careResult.textContent = "Upload a plant photo first.";
        return;
    }

    // Use the top prediction from the identification results.
    const firstPrediction = document.querySelector("#plant-result p");

    if (!firstPrediction) {
        careResult.textContent = "Identify the plant first.";
        return;
    }

    const plant = firstPrediction.textContent
        .replace(/^\d+\.\s*/, "")
        .split(" — ")[0];

    careButton.disabled = true;
    careResult.textContent = "Preparing your plant care guide...";

    try {
        const response = await fetch("/api/care", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ plant })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not get care advice.");
        }

        careResult.textContent = data.advice;
    } catch (error) {
        careResult.textContent = error.message;
    } finally {
        careButton.disabled = false;
    }
});


const plannerForm = document.getElementById("planner-form");
const plannerResult = document.getElementById("planner-result");
const plannerButton = document.getElementById("planner-button");

plannerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const location = document.getElementById("garden-location").value.trim();
    const season = document.getElementById("garden-season").value;
    const space = document.getElementById("garden-space").value;

    if (!location) {
        plannerResult.textContent = "Please enter your location.";
        return;
    }

    plannerButton.disabled = true;
    plannerButton.textContent = "Planning your garden...";
    plannerResult.textContent = "Your local AI is preparing suggestions... 🌱";

    try {
        const response = await fetch("/api/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ location, season, space })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not create your plan.");
        }

        // Display model output as plain text, not executable HTML.
        plannerResult.textContent = data.plan;
    } catch (error) {
        plannerResult.textContent = error.message;
    } finally {
        plannerButton.disabled = false;
        plannerButton.textContent = "Create my planting plan";
    }
});

