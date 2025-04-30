/**
 * Webcam management for Smart Mess Management System
 */

// Webcam variables
let stream = null;
let webcamVideo = null;
let capturedImage = null;

/**
 * Initialize webcam for face detection
 * @param {string} videoElementId - ID of the video element
 * @param {string} canvasElementId - ID of the canvas element for captures
 * @param {string} startButtonId - ID of the start button
 * @param {string} captureButtonId - ID of the capture button
 * @param {string} imageDataInputId - ID of the hidden input for the image data
 */
function initWebcam(videoElementId, canvasElementId, startButtonId, captureButtonId, imageDataInputId) {
    webcamVideo = document.getElementById(videoElementId);
    const canvas = document.getElementById(canvasElementId);
    const startButton = document.getElementById(startButtonId);
    const captureButton = document.getElementById(captureButtonId);
    const imageDataInput = document.getElementById(imageDataInputId);

    if (!webcamVideo || !canvas || !startButton || !captureButton || !imageDataInput) {
        console.error('Missing required elements for webcam initialization');
        return;
    }

    // Start webcam
    startButton.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            webcamVideo.srcObject = stream;
            webcamVideo.style.display = 'block';
            startButton.style.display = 'none';
            captureButton.style.display = 'inline-block';
        } catch (err) {
            console.error('Error accessing webcam:', err);
            alert('Error accessing webcam. Please ensure your browser has permission to use the camera.');
        }
    });

    // Capture image
    captureButton.addEventListener('click', () => {
        // Capture the image
        const context = canvas.getContext('2d');
        canvas.width = webcamVideo.videoWidth;
        canvas.height = webcamVideo.videoHeight;
        context.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to base64 for sending to server
        capturedImage = canvas.toDataURL('image/jpeg');
        imageDataInput.value = capturedImage;
        
        // Display the captured image
        canvas.style.display = 'block';
        webcamVideo.style.display = 'none';
        
        // Change button to recapture
        captureButton.textContent = 'Recapture';
        captureButton.addEventListener('click', () => {
            canvas.style.display = 'none';
            webcamVideo.style.display = 'block';
            captureButton.textContent = 'Capture';
        }, { once: true });
    });
}

/**
 * Stop the webcam stream
 */
function stopWebcam() {
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        stream = null;
    }
}

/**
 * Clean up webcam resources when leaving the page
 */
window.addEventListener('beforeunload', () => {
    stopWebcam();
});
