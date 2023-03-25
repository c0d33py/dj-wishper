const speechButton = document.getElementById("speechStart");
const outputElement = document.getElementById("output");
const recognition = new window.webkitSpeechRecognition();

recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

speechButton.addEventListener("mousedown", function () {
    this.classList.add("btn-outline-danger");
    this.classList.remove("btn-outline-light");
    this.textContent = 'Stop'
    // recognition.start();
});

speechButton.addEventListener("mouseup", () => {
    speechButton.classList.remove("btn-outline-danger");
    speechButton.classList.add("btn-outline-light");
    speechButton.textContent = 'Speech'

    // recognition.stop();
});

recognition.addEventListener("result", function (event) {
    const result = event.results[event.results.length - 1][0].transcript;
    outputElement.textContent = result;
});