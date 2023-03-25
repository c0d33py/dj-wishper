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

// Get STT data
async function getSTTData() {
    const transcribeData = await fetchAPI()
    transcribeData.forEach((item) => {
        outputWrapper.innerHTML += `
            <div class="stt-data">
                <p class="ur">${item.transcript}</p>
                <button type="button" class="delete-transcript-btn" date-target="${item.id}">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M5.05063 8.73418C4.20573 7.60763 5.00954 6 6.41772 6H17.5823C18.9905 6 19.7943 7.60763 18.9494 8.73418V8.73418C18.3331 9.55584 18 10.5552 18 11.5823V18C18 20.2091 16.2091 22 14 22H10C7.79086 22 6 20.2091 6 18V11.5823C6 10.5552 5.66688 9.55584 5.05063 8.73418V8.73418Z"
                            stroke="white" stroke-width="1.5" />
                        <path opacity="0.3" d="M14 17L14 11" stroke="white" stroke-width="1.5" stroke-linecap="round"
                            stroke-linejoin="round" />
                        <path opacity="0.3" d="M10 17L10 11" stroke="white" stroke-width="1.5" stroke-linecap="round"
                            stroke-linejoin="round" />
                        <path opacity="0.3"
                            d="M16 6L15.4558 4.36754C15.1836 3.55086 14.4193 3 13.5585 3H10.4415C9.58066 3 8.81638 3.55086 8.54415 4.36754L8 6"
                            stroke="white" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                </button>
            </div>`;
    });
};

// Delete transcript
outputWrapper.addEventListener('click', async (event) => {
    // check if the clicked element is a delete button
    if (event.target.classList.contains('delete-transcript-btn') || event.target.closest('.delete-transcript-btn')) {
        const targetId = event.target.closest('.delete-transcript-btn').getAttribute('date-target');
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

// On load
getSTTData();