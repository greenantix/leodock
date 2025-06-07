// Main JavaScript file for LeoDock Enhanced Platform

// --- LEO Supervisor Functions ---
function updateLEOActivity() {
    fetch('/api/leo/activity')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('leo-status-text').textContent = 'Offline';
                document.getElementById('leo-status-dot').style.color = 'red';
                return;
            }

            // Update status
            const status = data.current_status;
            document.getElementById('leo-status-text').textContent = status.status;
            document.getElementById('leo-status-dot').style.color = status.status === 'idle' ? 'green' : 'orange';
            document.getElementById('leo-current-task').textContent = status.current_task || 'No active task';

            // Update activity feed
            const activityList = document.getElementById('leo-activity-list');
            activityList.innerHTML = '';
            
            data.recent_activities.slice(-10).reverse().forEach(activity => {
                const activityDiv = document.createElement('div');
                activityDiv.className = `activity-item importance-${activity.importance}`;
                
                const timeSpan = document.createElement('span');
                timeSpan.className = 'activity-time';
                timeSpan.textContent = activity.time_friendly;
                
                const descSpan = document.createElement('span');
                descSpan.className = 'activity-description';
                descSpan.textContent = activity.description;
                
                activityDiv.appendChild(timeSpan);
                activityDiv.appendChild(descSpan);
                activityList.appendChild(activityDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching LEO activity:', error);
            document.getElementById('leo-status-text').textContent = 'Error';
            document.getElementById('leo-status-dot').style.color = 'red';
        });
}

function chatWithLEO() {
    const messageInput = document.getElementById('leo-message');
    const chatOutput = document.getElementById('leo-chat-output');
    const message = messageInput.value.trim();
    
    if (!message) {
        alert('Please enter a message for LEO');
        return;
    }
    
    // Add user message to chat
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user-message';
    userDiv.textContent = `You: ${message}`;
    chatOutput.appendChild(userDiv);
    
    messageInput.value = '';
    
    // Send to LEO
    fetch('/api/leo/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        const leoDiv = document.createElement('div');
        leoDiv.className = 'chat-message leo-message';
        leoDiv.textContent = `LEO: ${data.leo_response || data.error}`;
        chatOutput.appendChild(leoDiv);
        chatOutput.scrollTop = chatOutput.scrollHeight;
        
        // Refresh activity after chat
        setTimeout(updateLEOActivity, 1000);
    })
    .catch(error => {
        console.error('Error chatting with LEO:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message error-message';
        errorDiv.textContent = 'Error communicating with LEO';
        chatOutput.appendChild(errorDiv);
    });
}

function generateCLAUDEmd() {
    fetch('/api/leo/generate_claude_md')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`CLAUDE.md generated successfully!\nSaved as: ${data.file}`);
                // Update activity to show this action
                setTimeout(updateLEOActivity, 1000);
            } else {
                alert(`Error generating CLAUDE.md: ${data.error}`);
            }
        })
        .catch(error => {
            alert('Error generating CLAUDE.md: ' + error);
        });
}

function viewLEOLogs() {
    // Open LEO activity in a new window or modal
    window.open('/api/leo/activity', '_blank');
}

// Initialize LEO activity updates
document.addEventListener('DOMContentLoaded', function() {
    // Initial load
    updateLEOActivity();
    
    // Update every 5 seconds  
    setInterval(updateLEOActivity, 5000);
    
    // Update header status
    setInterval(function() {
        fetch('/api/leo/status')
            .then(response => response.json())
            .then(data => {
                const headerStatus = document.getElementById('header-leo-status');
                if (data.error) {
                    headerStatus.textContent = 'Offline';
                    headerStatus.style.color = 'red';
                } else {
                    headerStatus.textContent = 'Active';
                    headerStatus.style.color = 'green';
                }
            })
            .catch(() => {
                const headerStatus = document.getElementById('header-leo-status');
                headerStatus.textContent = 'Error';
                headerStatus.style.color = 'red';
            });
    }, 10000);
});

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