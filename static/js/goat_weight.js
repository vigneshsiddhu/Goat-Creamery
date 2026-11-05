document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("goat-weight-form");
    const goatSelect = document.getElementById("id_goat");
    let weightInput = document.getElementById("id_weight");
    const confirmationPopup = document.getElementById("weight-voice-confirmation");
    const voiceText = document.getElementById("weight-voice-text");
    const confirmationGoat = document.getElementById("weight-confirmation-goat");
    const confirmationWeight = document.getElementById("weight-confirmation-value");
    const changeButton = document.getElementById("weight-confirmation-cancel");
    const saveButton = document.getElementById("weight-confirmation-save");
    const confirmButtons = document.querySelectorAll("[data-weight-confirm]");
    const displayValue = document.getElementById("weight-display-value");
    const displayGoat = document.getElementById("weight-display-goat");
    const keypad = document.getElementById("weight-keypad");
    const keypadDisplay = document.getElementById("weight-keypad-display");

    const MIN_WEIGHT = 0.1;
    const MAX_WEIGHT = 80;

    if (!form || !goatSelect) {
        return;
    }

    if (!weightInput) {
        weightInput = document.createElement("input");
        weightInput.type = "hidden";
        weightInput.name = "weight";
        weightInput.id = "id_weight";
        form.appendChild(weightInput);
    }

    let typingBuffer = "";
    let typingMode = false;
    let currentWeight = 0;

    if (window.speechSynthesis) {
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = function () {
            window.speechSynthesis.getVoices();
        };
    }

    function clampWeight(value) {
        if (isNaN(value)) return 0;
        return Math.min(MAX_WEIGHT, Math.max(0, Math.round(value * 10) / 10));
    }

    function formatWeight(value) {
        return clampWeight(value).toFixed(1);
    }

    function setDisplay(text) {
        if (displayValue) displayValue.textContent = text || "0";
    }

    function setTyping(isTyping) {
        if (keypadDisplay) keypadDisplay.classList.toggle("is-typing", isTyping);
    }

    function commitWeight(value) {
        typingMode = false;
        typingBuffer = "";
        setTyping(false);
        currentWeight = clampWeight(value);
        setDisplay(formatWeight(currentWeight));
        weightInput.value = currentWeight >= MIN_WEIGHT ? formatWeight(currentWeight) : "";
    }

    function updateFromBuffer() {
        setTyping(true);
        setDisplay(typingBuffer || "0");
        const parsed = parseFloat(typingBuffer);
        if (isNaN(parsed)) {
            currentWeight = 0;
            weightInput.value = "";
            return;
        }
        currentWeight = clampWeight(parsed);
        weightInput.value = currentWeight >= MIN_WEIGHT ? formatWeight(currentWeight) : "";
    }

    function getSelectedGoat() {
        if (!goatSelect.value) return null;
        const option = goatSelect.options[goatSelect.selectedIndex];
        if (!option) return null;
        return { value: goatSelect.value, text: option.textContent.trim() };
    }

    function getSelectedWeight() {
        const value = parseFloat(weightInput.value);
        if (isNaN(value) || value < MIN_WEIGHT) return null;
        return { value: formatWeight(value), text: formatWeight(value) };
    }

    function speakMessage(tamilText, englishText) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const voices = window.speechSynthesis.getVoices() || [];
        const tamilVoice = voices.find(function (voice) {
            return (voice.lang || "").toLowerCase().indexOf("ta") === 0;
        });
        const utterance = new SpeechSynthesisUtterance(tamilVoice ? tamilText : englishText);
        utterance.lang = tamilVoice ? (tamilVoice.lang || "ta-IN") : "en-IN";
        utterance.rate = 0.9;
        if (tamilVoice) utterance.voice = tamilVoice;
        window.speechSynthesis.speak(utterance);
    }

    function applyGoatSelection() {
        const goat = getSelectedGoat();
        if (!goat) {
            if (displayGoat) displayGoat.textContent = "Select Token ID";
            return;
        }
        if (displayGoat) displayGoat.textContent = goat.text;
        const option = goatSelect.options[goatSelect.selectedIndex];
        const lastWeight = parseFloat(option.getAttribute("data-last-weight"));
        if (!isNaN(lastWeight) && lastWeight > 0) {
            commitWeight(lastWeight);
        }
    }

    function openConfirmation() {
        const goat = getSelectedGoat();
        const weight = getSelectedWeight();
        if (!goat) {
            if (displayGoat) displayGoat.textContent = "Select Token ID first";
            goatSelect.focus();
            return;
        }
        if (!weight) {
            if (displayGoat) displayGoat.textContent = goat.text + " · enter kg";
            return;
        }

        confirmationGoat.textContent = goat.text;
        confirmationWeight.textContent = weight.text + " kg";
        const tamilMessage = "எடை " + weight.text + " கிலோ. சரியா?";
        const englishMessage = "Weight " + weight.text + " kilogram. Confirm?";
        if (voiceText) voiceText.textContent = tamilMessage;
        if (confirmationPopup) {
            confirmationPopup.classList.add("is-open");
            confirmationPopup.style.display = "flex";
        }
        document.body.style.overflow = "hidden";
        speakMessage(tamilMessage, englishMessage);
    }

    function closeConfirmation() {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (confirmationPopup) {
            confirmationPopup.classList.remove("is-open");
            confirmationPopup.style.display = "none";
        }
        document.body.style.overflow = "";
    }

    function submitForm() {
        const goat = getSelectedGoat();
        const weight = getSelectedWeight();
        if (!goat || !weight) return;
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        weightInput.value = weight.value;
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.textContent = "Saving...";
        }
        if (typeof form.requestSubmit === "function") {
            form.requestSubmit();
        } else {
            form.submit();
        }
    }

    goatSelect.addEventListener("change", applyGoatSelection);

    if (keypad) {
        keypad.addEventListener("click", function (event) {
            const button = event.target.closest("[data-key]");
            if (!button) return;
            const key = button.getAttribute("data-key");

            if (!typingMode) {
                typingBuffer = "";
                typingMode = true;
            }

            if (key === "back") {
                typingBuffer = typingBuffer.slice(0, -1);
            } else if (key === ".") {
                if (typingBuffer.indexOf(".") === -1) {
                    typingBuffer = typingBuffer ? typingBuffer + "." : "0.";
                }
            } else {
                const parts = typingBuffer.split(".");
                if (parts[1] && parts[1].length >= 1) return;
                if (parts[0].replace(/^0+/, "").length >= 2 && typingBuffer.indexOf(".") === -1) return;
                typingBuffer += key;
            }
            updateFromBuffer();
        });
    }

    confirmButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            openConfirmation();
        });
    });

    if (changeButton) {
        changeButton.addEventListener("click", function (event) {
            event.preventDefault();
            closeConfirmation();
        });
    }

    if (saveButton) {
        saveButton.addEventListener("click", function (event) {
            event.preventDefault();
            submitForm();
        });
    }

    form.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            openConfirmation();
        }
    });

    if (confirmationPopup) {
        confirmationPopup.addEventListener("click", function (event) {
            if (event.target === confirmationPopup) closeConfirmation();
        });
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeConfirmation();
    });

    window.addEventListener("beforeunload", function () {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    });

    commitWeight(0);
    applyGoatSelection();
});
