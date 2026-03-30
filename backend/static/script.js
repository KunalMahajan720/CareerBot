function toggleChat() {
  const chatBody = document.getElementById("chat-body");
  const icon = document.getElementById("toggle-icon");
  chatBody.style.display = chatBody.style.display === "flex" ? "none" : "flex";
  icon.innerHTML = chatBody.style.display === "flex" ? "&#9650;" : "&#9660;";
}

function getTimeStamp() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function addMessage(message, sender) {
  const messages = document.getElementById("messages");
  const msgDiv = document.createElement("div");
  msgDiv.className = "message " + (sender === "user" ? "user-msg" : "bot-msg");
  msgDiv.innerHTML = `<span>${message.replace(/\n/g, "<br>")}</span><span class="timestamp">${getTimeStamp()}</span>`;
  messages.appendChild(msgDiv);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => addMessage(data.response, "bot"))
    .catch(err => addMessage("Error contacting server.", "bot"));
}

function startListening() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value = transcript;
    sendMessage();
  };

  recognition.onerror = () => {
    addMessage("Sorry, voice input failed. Try typing instead.", "bot");
  };
}

function uploadResume() {
  const fileInput = document.getElementById("resume-upload");
  const file = fileInput.files[0];
  if (!file) {
    addMessage("Please select a resume file to upload.", "bot");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  fetch("/upload_resume", {
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      let feedback = "**📄 Resume Feedback**\n";
      feedback += `📧 Email: ${data.email || "Not found"}\n`;
      feedback += `📱 Phone: ${data.phone || "Not found"}\n`;
      feedback += `🛠 Skills: ${data.skills?.join(", ") || "Not found"}\n`;
      feedback += `💡 Suggestions: ${data.suggestions || "None"}`;
      addMessage(feedback, "bot");
    })
    .catch(() => {
      addMessage("There was an error uploading the resume.", "bot");
    });
}
function displayFileName() {
  const fileInput = document.getElementById("resume-upload");
  const fileNameSpan = document.getElementById("file-name");

  if (fileInput.files.length > 0) {
    fileNameSpan.textContent = fileInput.files[0].name;
  } else {
    fileNameSpan.textContent = "No file chosen";
  }
}
async function getQAResponse(question) {
  const response = await fetch("http://127.0.0.1:8000/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
  });

  const data = await response.json();
  return data.answer || "Sorry, I couldn't find an answer.";
}

