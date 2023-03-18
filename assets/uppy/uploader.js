"use strict";

const fileInput = document.getElementById('media-uuid')
const windowPath = window.location.href;

function stripQueryStringAndHashFromPath(URL) {
    return URL.split("vnr")[0].split("#")[0];
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


let _idArray = []
function getFiles(id) {
    _idArray.push(id)
    fileInput.value = _idArray
};

var uppy = new Uppy.Core({
    debug: false,
    allowMultipleUploadBatches: true,
    autoProceed: true,
    restrictions: {
        allowedFileTypes: ['image/*', 'video/*', '.mkv',],
    },
})
    .use(Uppy.Dashboard, {
        inline: true,
        target: '#drag-drop-area',
        proudlyDisplayPoweredByUppy: false,
        showProgressDetials: true,
        hideUploadButton: true,
        hideProgressAfterFinish: true,
        hideCancelButton: true,
        showRemoveButtonAfterComplete: true,
    })
    .use(Uppy.Tus, {
        endpoint: stripQueryStringAndHashFromPath(windowPath) + "api/upload/",
        headers: { 'X-CSRFToken': csrftoken },
        chunkSize: parseInt(5242880, 10),
        retryDelays: [0, 1000, 3000, 5000],
        fileDate: true,
        fileName: 'file'
    })
uppy.on('complete', result => {
    result.successful.forEach(index => {
        console.log(index.response.uploadURL)
        var file_id = /[^/]*$/.exec(index.response.uploadURL)[0];
        getFiles(file_id);
    });
});
uppy.on('file-removed', (file, reason) => {
    sendDeleteRequestForFile(file)
})
uppy.reset()

function sendDeleteRequestForFile(file) {
    var file_id = /[^/]*$/.exec(file.uploadURL)[0];
    var url = stripQueryStringAndHashFromPath(windowPath) + "api/upload/delete/" + file_id;
    var xhr = new XMLHttpRequest();
    xhr.open('DELETE', url, true);
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.send();
}


// var uploadBtn = $(id + ' .uppy-btn');
// uploadBtn.click(function () {
//     uppyDrag.upload();
// });
