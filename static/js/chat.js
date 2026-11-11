const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const btnClear = document.getElementById("btn-clear");
const learnMode = document.getElementById("learn-mode");

function addMessage(sender, text, meta) {
  const row = document.createElement("div");
  row.className = `msg msg-${sender}`;
  if (sender === "bot") {
    const avatar = document.createElement("span");
    avatar.className = "msg-avatar";
    avatar.textContent = THEME.avatar;
    row.appendChild(avatar);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  if (meta) {
    const small = document.createElement("small");
    small.className = "meta";
    small.textContent = meta;
    bubble.appendChild(small);
  }
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

async function showCandidates(bubble, text) {
  const response = await fetch("/api/explain", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text, theme: THEME.id})
  });
  const data = await response.json();
  if (!response.ok) return;
  const list = document.createElement("ol");
  list.className = "candidates";
  data.candidates.forEach((candidate) => {
    const item = document.createElement("li");
    const status = candidate.score >= data.threshold ? "lolos ambang" : "di bawah ambang";
    item.textContent = `${candidate.intent} · ${candidate.score.toFixed(2)} (${status}) · pola: "${candidate.pattern}"`;
    list.appendChild(item);
  });
  bubble.appendChild(list);
}

async function sendMessage(text) {
  addMessage("user", text);
  const typing = addMessage("bot", "GiftMate sedang berpikir...");
  input.disabled = true;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text, theme: THEME.id})
    });
    const data = await response.json();
    typing.parentElement.remove();
    if (!response.ok) {
      addMessage("bot", data.error || "Pesan gagal diproses.");
      return;
    }
    const meta = data.intent ? `intent: ${data.intent} · skor ${data.score.toFixed(2)}` : `fallback · skor ${data.score.toFixed(2)}`;
    const bubble = addMessage("bot", data.reply, meta);
    if (learnMode.checked) await showCandidates(bubble, text);
  } catch (error) {
    typing.parentElement.remove();
    addMessage("bot", "Tidak dapat terhubung ke server. Pastikan aplikasi Flask masih berjalan.");
  } finally {
    input.disabled = false;
    input.focus();
  }
}

async function loadHistory() {
  try {
    const response = await fetch(`/api/history/${THEME.id}`);
    const rows = await response.json();
    if (!rows.length) {
      addMessage("bot", THEME.greeting);
      return;
    }
    rows.forEach((row) => addMessage(row.sender, row.text));
  } catch (error) {
    addMessage("bot", THEME.greeting);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent));
});

btnClear.addEventListener("click", async () => {
  await fetch(`/api/history/${THEME.id}`, {method: "DELETE"});
  messagesEl.replaceChildren();
  addMessage("bot", THEME.greeting);
});

loadHistory();
