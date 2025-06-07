// Main JavaScript file for LeoDock Enhanced Platform

// --- LLM Panel Logic ---
function sendToLLM() {
    const promptInput = document.getElementById('llm-prompt');
    const llmOutput = document.getElementById('llm-output');
    const llmSelector = document.getElementById('llm-selector');

    const prompt = promptInput.value;
    const selectedLLM = llmSelector.value;

    if (!prompt.trim()) {
        alert("Please enter a prompt.");
        return;
    }

    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('message', 'user-message');
    userMessageDiv.textContent = `You: ${prompt}`;
    llmOutput.appendChild(userMessageDiv);
    promptInput.value = '';
    llmOutput.scrollTop = llmOutput.scrollHeight;

    fetch('/api/llm/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            llm_type: selectedLLM,
            prompt: prompt,
            context: "" // Future: Add context from editor or conversation
        }),
    })
    .then(response => response.json())
    .then(data => {
        const llmMessageDiv = document.createElement('div');
        llmMessageDiv.classList.add('message', 'llm-message');
        if (data.error) {
            llmMessageDiv.textContent = `Error: ${data.error}`;
        } else if (data.choices && data.choices.length > 0 && data.choices[0].message) {
            llmMessageDiv.textContent = `${selectedLLM}: ${data.choices[0].message.content}`;
        } else {
            llmMessageDiv.textContent = `${selectedLLM}: No response or unexpected format.`;
            console.log("Unexpected LLM response format:", data);
        }
        llmOutput.appendChild(llmMessageDiv);
        llmOutput.scrollTop = llmOutput.scrollHeight;
    })
    .catch((error) => {
        console.error('Error sending to LLM:', error);
        const errorMessageDiv = document.createElement('div');
        errorMessageDiv.classList.add('message', 'error-message');
        errorMessageDiv.textContent = `Network or server error: ${error}`;
        llmOutput.appendChild(errorMessageDiv);
        llmOutput.scrollTop = llmOutput.scrollHeight;
    });
}

// --- Chat History Logic ---
function searchHistory() {
    const searchInput = document.getElementById('search-input');
    const historyList = document.getElementById('history-list');
    const query = searchInput.value;

    fetch(`/api/history/search?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        historyList.innerHTML = ''; // Clear previous results
        if (data.length === 0) {
            historyList.innerHTML = '<p>No conversations found.</p>';
        } else {
            const ul = document.createElement('ul');
            ul.style.listStyleType = 'none';
            ul.style.paddingLeft = '0';
            data.forEach(conv => {
                const li = document.createElement('li');
                li.style.marginBottom = '10px';
                li.style.padding = '5px';
                li.style.border = '1px solid #eee';
                li.innerHTML = `
                    <strong>${new Date(conv.timestamp).toLocaleString()}</strong> (Session: ${conv.session_id || 'N/A'})<br>
                    <em>Prompt:</em> ${conv.prompt}<br>
                    <em>Response:</em> ${conv.response}
                `;
                ul.appendChild(li);
            });
            historyList.appendChild(ul);
        }
    })
    .catch(error => {
        console.error('Error searching history:', error);
        historyList.innerHTML = '<p>Error loading search results.</p>';
    });
}

function exportHistory() {
    alert("Export history functionality not yet implemented.");
}

// --- Terminal and Communication Logic ---
function restartTerminal() {
    const terminalFrame = document.querySelector('.terminal-frame');
    if (terminalFrame) {
        // Simple iframe reload. For a true process restart, backend interaction is needed.
        terminalFrame.src = terminalFrame.src;
        alert("Terminal iframe reloaded. For a full restart, server-side implementation is required.");
    } else {
        alert("Terminal iframe not found.");
    }
}

function clearTerminal() {
    // This is tricky. True clear usually involves sending control characters (e.g., Ctrl+L)
    // or specific commands to the shell inside the terminal.
    // pyxtermjs might have an API for this, or it might need to be proxied.
    alert("Client-side clear is not directly available. Try typing 'clear' in the terminal.");
}

document.addEventListener('DOMContentLoaded', () => {
    // LLM Panel
    const llmSendButton = document.querySelector('.llm-input-area button'); // More robust selector needed if multiple buttons
    if (llmSendButton && llmSendButton.onclick === null) { // Check if onclick is not already set by HTML
         llmSendButton.onclick = sendToLLM;
    }
    const llmPromptTextarea = document.getElementById('llm-prompt');
    if (llmPromptTextarea) {
        llmPromptTextarea.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendToLLM();
            }
        });
    }

    // Chat History
    const historySearchButton = document.querySelector('.history-controls button[onclick="searchHistory()"]');
    // onclick is set in HTML, no need to re-attach unless we remove it from HTML.
    const historyExportButton = document.querySelector('.history-controls button[onclick="exportHistory()"]');
    // onclick is set in HTML.
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                searchHistory();
            }
        });
    }
    // Load initial history (e.g., last 5 items or no search query)
    searchHistory(); 

    // Communication/System
    const startCollaborationButton = document.getElementById('start-collaboration');
    if (startCollaborationButton) {
        startCollaborationButton.addEventListener('click', () => {
            alert('LLM Collaboration feature not yet implemented.');
        });
    }

    const viewLogsButton = document.getElementById('view-logs');
    if (viewLogsButton) {
        viewLogsButton.addEventListener('click', () => {
            alert('View Logs feature not yet implemented. Logs are in data/logs/ on the server.');
        });
    }
    
    // Terminal controls are already wired via onclick in HTML.
    // If we wanted to do it here:
    // const restartTerminalButton = document.querySelector('.terminal-controls button[onclick="restartTerminal()"]');
    // if(restartTerminalButton) restartTerminalButton.onclick = restartTerminal; // This would override HTML
    // const clearTerminalButton = document.querySelector('.terminal-controls button[onclick="clearTerminal()"]');
    // if(clearTerminalButton) clearTerminalButton.onclick = clearTerminal; // This would override HTML
});