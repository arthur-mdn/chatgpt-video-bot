// popup.js
document.getElementById('sendButton').addEventListener('click', function() {
    const prompts = document.getElementById('promptInput').value;
    try {
        const promptsJson = JSON.parse(prompts);
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            console.log("Envoi du message au script de contenu");
            chrome.tabs.sendMessage(tabs[0].id, {type: "PROMPTS", data: promptsJson});
        });

    } catch (e) {
        alert('Erreure de JSON: ' + e.message);
    }
});

document.getElementById('downloadButton').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {type: "DOWNLOAD"});
    });
});