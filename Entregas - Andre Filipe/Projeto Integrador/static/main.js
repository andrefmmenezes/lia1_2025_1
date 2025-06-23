const allElem = {
  uploadSection: document.getElementById("upload-section"),
  audioFileInput: document.getElementById("audio-file-input"),
  fileNameDisplay: document.getElementById("file-name-display"),
  transcribeBtn: document.getElementById("transcribe-btn"),
  summarizeBtn: document.getElementById("summarize-btn"),
  suggestBtn: document.getElementById("suggest-btn"),
  loadingArea: document.getElementById("loading-area"),
  loadingText: document.getElementById("loading-text"),
  resultsArea: document.getElementById("results-area"),
  transcriptionOutput: document.getElementById("transcription-output"),
  transcriptionText: document.getElementById("transcription-text"),
  summaryOutput: document.getElementById("summary-output"),
  summaryText: document.getElementById("summary-text"),
  topicsOutput: document.getElementById("topics-output"),
  topicsList: document.getElementById("topics-list"),
  suggestionsOutput: document.getElementById("suggestions-output"),
  suggestionsList: document.getElementById("suggestions-list"),
  errorMessage: document.getElementById("error-message"),
  errorText: document.getElementById("error-text"),
  audioInput: document.getElementById('audio-file-input'),
  audioPlayer: document.getElementById('audio-player'),
};

let audioFile = null,
  fullTranscription = "";
function handleFile(file) {
  if (file && file.type.startsWith("audio/")) {
    audioFile = file;
    allElem.fileNameDisplay.textContent = audioFile.name;
    allElem.transcribeBtn.disabled = false;
    allElem.audioPlayer.src = URL.createObjectURL(file);
    allElem.audioPlayer.classList.remove("hidden");
    allElem.audioPlayer.classList.add("fade-in");
    allElem.audioPlayer.load();
    resetState();
  } else {
    audioFile = null;
    allElem.fileNameDisplay.textContent =
      "Arquivo inválido. Por favor, selecione um áudio.";
    allElem.transcribeBtn.disabled = true;
    allElem.audioPlayer.classList.add("hidden");
    allElem.audioPlayer.classList.remove("fade-in");
    allElem.audioPlayer.src = "";
  }
}
allElem.audioFileInput.addEventListener("change", (e) =>
  handleFile(e.target.files[0])
);
allElem.uploadSection.addEventListener("dragover", (e) => {
  e.preventDefault();
  allElem.uploadSection.classList.add("drag-over");
});
allElem.uploadSection.addEventListener("dragleave", () =>
  allElem.uploadSection.classList.remove("drag-over")
);
allElem.uploadSection.addEventListener("drop", (e) => {
  e.preventDefault();
  allElem.uploadSection.classList.remove("drag-over");
  handleFile(e.dataTransfer.files[0]);
});

async function apiCall(endpoint, options) {
  try {
    const response = await fetch('/api'+endpoint, options);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Erro ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    showError(error.message);
    setLoading(false);
    throw error;
  }
}

async function handleTranscription() {
  if (!audioFile) return;
  hideResults();
  setLoading(true, "Transcrevendo o áudio, isso pode levar alguns minutos...");
  const formData = new FormData();
  formData.append("file", audioFile);
  try {
    const data = await apiCall("/transcribe/", {
      method: "POST",
      body: formData,
    });
    console.log("Transcrição recebida:", data);
    fullTranscription = data.ai_transcription;
    allElem.transcriptionText.innerHTML = fullTranscription.replace(
      /\\n/g,
      "<br>"
    );
    allElem.transcriptionOutput.classList.remove("hidden");
    allElem.summarizeBtn.disabled = false;
    allElem.suggestBtn.disabled = false;
    setLoading(false);
    allElem.resultsArea.classList.remove("hidden");
  } catch (error) {
    console.error("Falha na transcrição:", error);
  }
}

async function handleSummarization() {
  if (!fullTranscription) return;
  setLoading(true, "Gerando o resumo com IA...");
  try {
    const data = await apiCall("/summarize/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: fullTranscription }),
    });
    allElem.summaryText.textContent = data.summary;
    allElem.summaryOutput.classList.remove("hidden");
    setLoading(false);
  } catch (error) {
    console.error("Falha ao resumir:", error);
  }
}

async function handleTopics() {
  if (!fullTranscription) return;
  setLoading(true, "Gerando resumo e sugestões com IA...");
  try {
    await Promise.all([handleKeypoints(), handleTopicSuggestion()]);
    setLoading(false);
  } catch (error) {
    console.error("Falha ao gerar resumo e sugestões:", error);
  }
}

async function handleKeypoints() {
  try {
    const data = await apiCall("/keypoints/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: fullTranscription }),
    });
    allElem.topicsList.innerHTML = "";
    data.keypoints.forEach((keypoint) => {
      const li = document.createElement("li");
      li.className = "flex items-center p-3 rounded-lg bg-blue-50 border-blue-500 text-blue-800 leading-relaxed";
      li.innerHTML = `<span><i>${keypoint.timestamp}</i>  <b>${keypoint.text}</b></span>`;
      allElem.topicsList.appendChild(li);
    });
    allElem.topicsOutput.classList.remove("hidden");
  } catch (error) {
    console.error("Falha ao obter principais tópicos:", error);
  }
}

async function handleTopicSuggestion() {
  try {
    const data2 = await apiCall("/suggestions/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: fullTranscription }),
    });
    allElem.suggestionsList.innerHTML = "";
    data2.suggestions.forEach((suggestion) => {
      const li = document.createElement("li");
      li.className = "flex items-center bg-gray-100 p-3 rounded-lg";
      li.innerHTML = `${suggestion.icon}  <span>${suggestion.text}</span>`;
      allElem.suggestionsList.appendChild(li);
    });
    allElem.suggestionsOutput.classList.remove("hidden");
  } catch (error) {
    console.error("Falha ao sugerir tópicos:", error);
  }
}


allElem.transcribeBtn.addEventListener("click", handleTranscription);
allElem.summarizeBtn.addEventListener("click", handleSummarization);
allElem.suggestBtn.addEventListener("click", handleTopics);

function setLoading(isLoading, message = "") {
  allElem.errorMessage.classList.add("hidden");
  if (isLoading) {
    allElem.loadingArea.classList.remove("hidden");
    allElem.loadingText.textContent = message;
    allElem.transcribeBtn.disabled = true;
    allElem.summarizeBtn.disabled = true;
    allElem.suggestBtn.disabled = true;
  } else {
    allElem.loadingArea.classList.add("hidden");
    allElem.transcribeBtn.disabled = audioFile === null;
    if (fullTranscription) {
      allElem.summarizeBtn.disabled = false;
      allElem.suggestBtn.disabled = false;
    }
  }
}
function hideResults() {
  allElem.resultsArea.classList.add("hidden");
  allElem.transcriptionOutput.classList.add("hidden");
  allElem.summaryOutput.classList.add("hidden");
  allElem.topicsOutput.classList.add("hidden");
  allElem.suggestionsOutput.classList.add("hidden");
  allElem.errorMessage.classList.add("hidden");
}
function resetState() {
  hideResults();
  fullTranscription = "";
  allElem.summarizeBtn.disabled = true;
  allElem.suggestBtn.disabled = true;
}
function showError(message) {
  allElem.errorText.textContent = message;
  allElem.errorMessage.classList.remove("hidden");
}
