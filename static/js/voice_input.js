document.addEventListener("DOMContentLoaded", function () {

    console.log("Voice Input JS loaded");

    const startBtn = document.getElementById("voice-start-btn");
    const stopBtn = document.getElementById("voice-stop-btn");
    const resultBox = document.getElementById("voice-result");
    const statusBox = document.getElementById("voice-status");

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    // =====================================================
    // BROWSER SUPPORT
    // =====================================================

    if (!SpeechRecognition) {

        console.error("Speech Recognition not supported");

        if (statusBox) {
            statusBox.innerText =
                "Speech recognition is not supported in this browser.";
        }

        if (startBtn) {
            startBtn.disabled = true;
        }

        return;
    }

    // =====================================================
    // VARIABLES
    // =====================================================

    let recognition = null;
    let listening = false;

    // =====================================================
    // START BUTTON
    // =====================================================

    if (startBtn) {

        startBtn.addEventListener("click", function () {

            if (listening) {
                return;
            }

            console.log("Start Speaking clicked");

            recognition = new SpeechRecognition();

            // English India
            recognition.lang = "en-IN";

            /*
             * false is more reliable for Chrome.
             * We collect the complete result from the browser.
             */
            recognition.continuous = false;

            recognition.interimResults = false;

            recognition.maxAlternatives = 1;

            // =================================================
            // START
            // =================================================

            recognition.onstart = function () {

                console.log("Microphone started");

                listening = true;

                startBtn.style.display = "none";

                if (stopBtn) {
                    stopBtn.style.display = "inline-flex";
                }

                if (statusBox) {
                    statusBox.innerText =
                        "Listening... Please speak your expense.";
                }
            };

            // =================================================
            // RESULT
            // =================================================

            recognition.onresult = function (event) {

                console.log("Speech result received");

                let text = "";

                for (
                    let i = 0;
                    i < event.results.length;
                    i++
                ) {

                    text +=
                        event.results[i][0].transcript + " ";
                }

                text = text.trim();

                console.log("Recognized:", text);

                if (resultBox) {
                    resultBox.value = text;
                }

                if (statusBox) {
                    statusBox.innerText =
                        "Speech recognized.";
                }

                /*
                 * Send complete text to farm_expense.js
                 */
                document.dispatchEvent(
                    new CustomEvent(
                        "voiceTextReady",
                        {
                            detail: {
                                text: text
                            }
                        }
                    )
                );
            };

            // =================================================
            // ERROR
            // =================================================

            recognition.onerror = function (event) {

                console.error(
                    "Speech recognition error:",
                    event.error
                );

                listening = false;

                if (event.error === "not-allowed") {

                    statusBox.innerText =
                        "Microphone permission denied.";

                }
                else if (event.error === "no-speech") {

                    statusBox.innerText =
                        "No speech detected. Please try again.";

                }
                else {

                    statusBox.innerText =
                        "Speech recognition error: " +
                        event.error;
                }

                resetButtons();
            };

            // =================================================
            // END
            // =================================================

            recognition.onend = function () {

                console.log("Recognition ended");

                listening = false;

                resetButtons();
            };

            // =================================================
            // START RECOGNITION
            // =================================================

            try {

                recognition.start();

            }
            catch (error) {

                console.error(
                    "Recognition start error:",
                    error
                );

                listening = false;

                resetButtons();
            }

        });
    }

    // =====================================================
    // STOP BUTTON
    // =====================================================

    if (stopBtn) {

        stopBtn.addEventListener("click", function () {

            console.log("Stop clicked");

            if (recognition && listening) {

                try {
                    recognition.stop();
                }
                catch (error) {
                    console.error(error);
                }
            }

            listening = false;

            resetButtons();
        });
    }

    // =====================================================
    // RESET BUTTONS
    // =====================================================

    function resetButtons() {

        if (startBtn) {
            startBtn.style.display = "inline-flex";
        }

        if (stopBtn) {
            stopBtn.style.display = "none";
        }
    }

    resetButtons();

});