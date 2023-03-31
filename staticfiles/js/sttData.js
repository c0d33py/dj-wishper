'use strict';

// Global variables
const outputWrapper = document.querySelector('#output');
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Fetch API 
async function fetchAPI() {
    let url = '/api/files/';
    let res = await fetch(url);
    let data = await res.json();
    return data.results;
};

// Language check
function languageCheck() {
    const paragraphs = document.querySelectorAll('.stt-data p');
    for (let i = 0; i < paragraphs.length; i++) {
        const text = paragraphs[i].innerText;
        if (/^[a-zA-Z\s]+$/.test(text)) {
            paragraphs[i].classList.remove('ur');
        }
    }
};

export let loadInterval

export function loader(element) {
    element.textContent = ''

    loadInterval = setInterval(() => {
        // Update the text content of the loading indicator
        element.textContent += '.';

        // If the loading indicator has reached three dots, reset it
        if (element.textContent === '....') {
            element.textContent = '';
        }
    }, 300);
}

// Strip query string and hash from path
export function stripQueryStringAndHashFromPath(URL) {
    return URL.split("vnr")[0].split("#")[0];
};

// Type text animation
export function typeText(text) {
    const pTag = document.createElement('p');
    let index = 0;
    const interval = setInterval(() => {
        if (index < text.length) {
            pTag.textContent += text.charAt(index);
            index++;
        } else {
            clearInterval(interval);
        }
    }, 20);
    return pTag;
}

// Transcript stripe template
function transcriptStripe(data) {
    return (`
    <div class="stt-data">
        <p class="ur">${data.transcript}</p>
        <div class="stt-data__meta">
            <button type="button" class="copy-transcript-btn" data-target="${data.id}">
                <i class="iconex iconex-copy"></i>
            </button>
            <button type="button" class="delete-transcript-btn" date-target="${data.id}">
                <i class="iconex iconex-delete"></i>
            </button>
        </div>
    </div>
    `)
}

// Get STT data
async function getSTTData() {
    const transcribeData = await fetchAPI()
    transcribeData.forEach((data) => {
        outputWrapper.insertAdjacentHTML('beforeend', transcriptStripe(data));
    });
    languageCheck();
};

// On load
getSTTData();

// Delete transcript
outputWrapper.addEventListener('click', async (event) => {
    const deleteButton = event.target.closest('.delete-transcript-btn');
    // check if the clicked element is a delete button
    if (deleteButton) {
        const targetId = deleteButton.getAttribute('date-target');
        try {
            // send a DELETE request to the server to delete the object
            const response = await fetch(`/api/files/${targetId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });
            if (response.ok) {
                // remove the deleted object from the DOM
                const sttData = event.target.closest('.stt-data');
                sttData.parentNode.removeChild(sttData);
            }
        } catch (error) {
            console.error(error);
        }
    }
    const copyButton = event.target.closest('.copy-transcript-btn');
    if (copyButton) {
        const textToCopy = copyButton.closest('.stt-data').querySelector('p').textContent;
        try {
            await navigator.clipboard.writeText(textToCopy);
            console.log('Text copied to clipboard');
        } catch (err) {
            console.error('Failed to"></ copy text: ', err);
        }
    }
});

// Configure the settings
document.addEventListener('DOMContentLoaded', () => {
    const transcriptionChecked = JSON.parse(localStorage.getItem('transcriptionChecked'));
    const cudaChecked = JSON.parse(localStorage.getItem('cudaChecked'));

    if (transcriptionChecked !== null) {
        document.getElementById('transcription').checked = transcriptionChecked;
    }

    if (cudaChecked !== null) {
        document.getElementById('cudaCheck').checked = cudaChecked;
    }
});
