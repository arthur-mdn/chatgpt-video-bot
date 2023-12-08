// Fonctions principales
function sendNextPrompt(prompts, currentPromptIndex) {
    if (currentPromptIndex < prompts.length) {
        const prompt = prompts[currentPromptIndex];
        const inputField = document.querySelector('#prompt-textarea');
        const sendButton = document.querySelector('button[data-testid="send-button"]');

        if (inputField && sendButton) {
            inputField.value = prompt.text;
            const event = new Event('input', { bubbles: true });
            inputField.dispatchEvent(event);
            sendButton.click();
            waitForResponseOrError(prompts, currentPromptIndex);
        }
    }
}

function waitForResponseOrError(prompts, currentPromptIndex) {
    const checkInterval = setInterval(() => {
        console.log('Checking for response...');
        const responseImage = document.querySelector('img[alt="Generated by DALL·E"]');
        const retryButton = document.querySelector('button.btn-primary:has(> div.flex > svg[stroke="currentColor"])');
        const sendButton = document.querySelector('button[data-testid="send-button"]');

        if (responseImage && (sendButton)) {
            clearInterval(checkInterval);
            handleResponse(prompts, currentPromptIndex);
        } else if (retryButton) {
            clearInterval(checkInterval);
            handleError(prompts, currentPromptIndex, retryButton);
        }
    }, 1000);
}

function handleResponse(prompts, currentPromptIndex) {
    currentPromptIndex++;
    if (currentPromptIndex < prompts.length) {
        sendNextPrompt(prompts, currentPromptIndex);
    } else {
        downloadResultsAsJson();
    }
}

function handleError(prompts, currentPromptIndex, retryButton) {
    retryButton.click();
    setTimeout(() => {
        sendNextPrompt(prompts, currentPromptIndex);
    }, 3000);
}

function downloadResultsAsJson() {
    const results = [];
    let turnIndex = 2; // On commence à l'indice 2 car c'est là que débute la conversation

    while (true) {
        const promptSelector = `[data-testid="conversation-turn-${turnIndex}"] .text-message`;
        const responseSelector = `[data-testid="conversation-turn-${turnIndex + 1}"] .text-message`;
        const imageSelector = `[data-testid="conversation-turn-${turnIndex + 1}"] img[alt="Generated by DALL·E"]`;

        const promptElement = document.querySelector(promptSelector);
        const responseElement = document.querySelector(responseSelector);
        const imageElement = document.querySelector(imageSelector);

        if (!promptElement || !responseElement) break; // Arrêter la boucle si on ne trouve pas de nouveaux éléments

        const promptText = promptElement.textContent.trim();
        const responseText = responseElement.textContent.trim();
        const imageUrl = imageElement ? imageElement.src : 'Image not found';

        results.push({
            prompt: promptText,
            response: responseText,
            imageUrl: imageUrl
        });

        turnIndex += 2; // Passer au prochain tour de conversation
    }
    console.log(results)
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(results));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "chatgpt_prompts_results.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}


// Gestionnaire de messages
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log("Message reçu dans le script de contenu", message);

    if (message.type === "PROMPTS") {
        sendNextPrompt(message.data, 0);
    } else if (message.type === "DOWNLOAD") {
        downloadResultsAsJson();
    }
});
