document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("goat-milk-form");
    const goatSelect = document.getElementById("id_goat");
    let milkInput = document.getElementById("id_milk_weight");
    const confirmationPopup = document.getElementById("milk-voice-confirmation");
    const voiceText = document.getElementById("milk-voice-text");
    const confirmationGoat = document.getElementById("milk-confirmation-goat");
    const confirmationMilk = document.getElementById("milk-confirmation-value");
    const changeButton = document.getElementById("milk-confirmation-cancel");
    const saveButton = document.getElementById("milk-confirmation-save");
    const confirmButtons = document.querySelectorAll("[data-milk-confirm]");
    const displayValue = document.getElementById("milk-display-value");
    const displayGoat = document.getElementById("milk-display-goat");
    const keypad = document.getElementById("milk-keypad");
    const keypadDisplay = document.getElementById("milk-keypad-display");

    const MIN_MILK = 0.1;
    const MAX_MILK = 5;

    if (!form || !goatSelect) {
        return;
    }

    if (!milkInput) {
        milkInput = document.createElement("input");
        milkInput.type = "hidden";
        milkInput.name = "milk_weight";
        milkInput.id = "id_milk_weight";
        form.appendChild(milkInput);
    }

    let typingBuffer = "";
    let typingMode = false;
    let currentMilk = 0;

    if (window.speechSynthesis) {
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = function () {
            window.speechSynthesis.getVoices();
        };
    }

    function clampMilk(value) {
        if (isNaN(value)) return 0;
        return Math.min(MAX_MILK, Math.max(0, Math.round(value * 10) / 10));
    }

    function formatMilk(value) {
        return clampMilk(value).toFixed(1);
    }

    function setDisplay(text) {
        if (displayValue) displayValue.textContent = text || "0";
    }

    function setTyping(isTyping) {
        if (keypadDisplay) keypadDisplay.classList.toggle("is-typing", isTyping);
    }

    function commitMilk(value) {
        typingMode = false;
        typingBuffer = "";
        setTyping(false);
        currentMilk = clampMilk(value);
        setDisplay(formatMilk(currentMilk));
        milkInput.value = currentMilk >= MIN_MILK ? formatMilk(currentMilk) : "";
    }

    function updateFromBuffer() {
        setTyping(true);
        setDisplay(typingBuffer || "0");
        const parsed = parseFloat(typingBuffer);
        if (isNaN(parsed)) {
            currentMilk = 0;
            milkInput.value = "";
            return;
        }
        currentMilk = clampMilk(parsed);
        milkInput.value = currentMilk >= MIN_MILK ? formatMilk(currentMilk) : "";
    }

    function getSelectedGoat() {
        if (!goatSelect.value) return null;
        const option = goatSelect.options[goatSelect.selectedIndex];
        if (!option) return null;
        return { value: goatSelect.value, text: option.textContent.trim() };
    }

    function getSelectedMilk() {
        const value = parseFloat(milkInput.value);
        if (isNaN(value) || value < MIN_MILK) return null;
        return { value: formatMilk(value), text: formatMilk(value) };
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
        const lastMilk = parseFloat(option.getAttribute("data-last-weight"));
        if (!isNaN(lastMilk) && lastMilk > 0) {
            commitMilk(lastMilk);
        }
    }

    function openConfirmation() {
        const goat = getSelectedGoat();
        const milk = getSelectedMilk();
        if (!goat) {
            if (displayGoat) displayGoat.textContent = "Select Token ID first";
            goatSelect.focus();
            return;
        }
        if (!milk) {
            if (displayGoat) displayGoat.textContent = goat.text + " · enter L";
            return;
        }

        confirmationGoat.textContent = goat.text;
        confirmationMilk.textContent = milk.text + " L";
        const tamilMessage = "பால் " + milk.text + " லிட்டர். சரியா?";
        const englishMessage = "Milk " + milk.text + " litre. Confirm?";
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
        const milk = getSelectedMilk();
        if (!goat || !milk) return;
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        milkInput.value = milk.value;
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
                if (parts[0].replace(/^0+/, "").length >= 1 && typingBuffer.indexOf(".") === -1) return;
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

    commitMilk(0);
    applyGoatSelection();
});
