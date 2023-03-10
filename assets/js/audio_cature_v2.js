// Request permission to access the user's microphone
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(function (stream) {
        // Create an AudioContext and a MediaStreamAudioSourceNode
        var audioContext = new AudioContext();
        var sourceNode = audioContext.createMediaStreamSource(stream);

        // Create an RTCPeerConnection object
        var pc = new RTCPeerConnection();

        // Add the local audio track to the connection
        sourceNode.connect(audioContext.destination);
        stream.getAudioTracks().forEach(function (track) {
            pc.addTrack(track, stream);
        });

        // Create an offer and send it to the remote server or client
        pc.createOffer()
            .then(function (offer) {
                return pc.setLocalDescription(offer);
            })
            .then(function () {
                // Send the offer using a signaling mechanism
                // such as WebSockets or HTTP
            });
    })
    .catch(function (error) {
        console.error('Failed to get user media', error);
    });
