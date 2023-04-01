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

// Strip query string and hash from path
export function stripQueryStringAndHashFromPath(URL) {
    return URL.split("vnr")[0].split("#")[0];
};

// Language check
export function languageCheck() {
    const paragraphs = document.querySelectorAll('.stt-data p');
    for (let i = 0; i < paragraphs.length; i++) {
        // Check if the text is in English remove the class 'ur' [a-zA-Z!@#$%^&*(),.?":{}|<>;'\[\]\\\/\s]
        const text = paragraphs[i].textContent;
        if (/^[a-zA-Z!@#$%^&*(),.?":{}|<>;'\[\]\\\/]+/.test(text)) {
            paragraphs[i].classList.remove('ur');
        }
        // Check the lines of text length
        const rect = paragraphs[i].getClientRects()[0];
        const lineHeight = parseInt(window.getComputedStyle(paragraphs[i]).lineHeight);
        const numLines = rect.height / lineHeight;
        // Get the next sibling element of the paragraph and remove the class
        if (numLines < 4) {
            let nextSibling = paragraphs[i].nextElementSibling;
            nextSibling.style.transform = "translate(102%, -50%)";
            const btnGroup = nextSibling.querySelector('.btn-group-vertical');
            btnGroup?.classList.replace('btn-group-vertical', 'btn-group');
        }
    }
};

// Create transcript stripe
export function transcriptStripe(data) {
    return (`
    <div class="stt-data" data-target="${data.id}">
        <p class="ur">${data.transcript}</p>
        <div class="stt-data__meta">
            <div class="btn-group-vertical" role="group" aria-label="Vertical button group">
                <button type="button" class="btn btn-default edit-transcript-btn">
                    <i class="iconex iconex-broken-pen1"></i></button>
                <button type="button" class="btn btn-default copy-transcript-btn">
                    <i class="iconex iconex-broken-copy"></i></button>
                <button type="button" class="btn btn-default delete-transcript-btn">
                    <i class="iconex iconex-broken-delete"></i></button>
            </div>
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
    const copyButton = event.target.closest('.copy-transcript-btn');
    const editButton = event.target.closest('.edit-transcript-btn');
    // Action on click of the buttons
    if (copyButton) {
        const textToCopy = copyButton.closest('.stt-data').querySelector('p').textContent;
        try {
            await navigator.clipboard.writeText(textToCopy);
            console.log('Text copied to clipboard');
        } catch (err) {
            console.error('Failed to"></ copy text: ', err);
        }
    }
    if (editButton) {
        const targetId = editButton.closest('.stt-data').dataset.target;
        let paragraph = editButton.closest('.stt-data').querySelector('p');
        paragraph.contentEditable = true;
        paragraph.classList.add('editing');
        // listen to the mousedown event on the document
        document.addEventListener('mousedown', ({ target }) => {
            if (!paragraph.contains(target)) {
                paragraph.contentEditable = false;
                paragraph.classList.remove('editing');
            }
        });
        paragraph.addEventListener('input', async (e) => {
            // send a PUT request to the server to delete the object on keyup
            const response = await fetch(`/api/files/${targetId}/`, {
                method: 'PUT',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    transcript: e.target.textContent,
                }),
            });
            if (response.ok) {
                console.log('Transcript updated');
            }
        });
    }
    if (deleteButton) {
        const targetId = deleteButton.closest('.stt-data').dataset.target;;
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
