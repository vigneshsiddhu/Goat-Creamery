document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("farm-expense-voice-form");
    const categorySelect = document.getElementById("id_category");
    const amountInput = document.getElementById("id_amount");
    const confirmationPopup = document.getElementById("expense-voice-confirmation");
    const voiceText = document.getElementById("expense-voice-text");
    const confirmationCategory = document.getElementById("expense-confirmation-category");
    const confirmationAmount = document.getElementById("expense-confirmation-amount");
    const changeButton = document.getElementById("expense-confirmation-cancel");
    const saveButton = document.getElementById("expense-confirmation-save");
    const confirmButtons = document.querySelectorAll("[data-expense-confirm]");

    if (!form || !categorySelect || !amountInput) return;

    amountInput.setAttribute("step", "1");
    amountInput.setAttribute("min", "1");
    amountInput.setAttribute("placeholder", "5000");
    amountInput.setAttribute("inputmode", "numeric");
    amountInput.addEventListener("input", function () {
        amountInput.value = amountInput.value.replace(/[^\d]/g, "");
    });

    if (window.speechSynthesis) {
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = function () {
            window.speechSynthesis.getVoices();
        };
    }

    function getSelectedCategory() {
        if (!categorySelect.value) return null;
        const option = categorySelect.options[categorySelect.selectedIndex];
        return { value: categorySelect.value, text: option ? option.textContent.trim() : categorySelect.value };
    }

    function getEnteredAmount() {
        const value = parseInt(amountInput.value, 10);
        if (isNaN(value) || value <= 0 || String(amountInput.value).indexOf(".") !== -1) return null;
        return { value: value, text: String(value) };
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

    function openConfirmation() {
        const category = getSelectedCategory();
        const amount = getEnteredAmount();
        if (!category) {
            categorySelect.focus();
            return;
        }
        if (!amount) {
            amountInput.focus();
            return;
        }
        if (confirmationCategory) confirmationCategory.textContent = category.text;
        if (confirmationAmount) confirmationAmount.textContent = "₹" + amount.text;
        const tamilMessage = category.text + " " + amount.text + " ரூபாய். சரியா?";
        const englishMessage = category.text + " " + amount.text + " rupees. Confirm?";
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
        const category = getSelectedCategory();
        const amount = getEnteredAmount();
        if (!category || !amount) return;
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        amountInput.value = amount.text;
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

    const shareOverlay = document.getElementById("expense-share-overlay");
    const shareDataNode = document.getElementById("last-saved-expense");
    const shareButton = document.getElementById("expense-share-button");
    const whatsappButton = document.getElementById("expense-share-whatsapp");
    const shareCloseButton = document.getElementById("expense-share-close");
    let savedExpense = null;

    if (shareDataNode) {
        try {
            savedExpense = JSON.parse(shareDataNode.textContent);
        } catch (error) {
            savedExpense = null;
        }
    }

    function getShareText() {
        if (!savedExpense) return "";
        return [
            "Farm Expense",
            "Date: " + savedExpense.date,
            "Category: " + savedExpense.category,
            "Amount: ₹" + savedExpense.amount,
        ].join("\n");
    }

    function closeShareOverlay() {
        if (!shareOverlay) return;
        shareOverlay.classList.remove("is-open");
        shareOverlay.style.display = "none";
        document.body.style.overflow = "";
    }

    function openWhatsAppShare() {
        const text = getShareText();
        if (!text) return;
        window.open("https://wa.me/?text=" + encodeURIComponent(text), "_blank");
    }

    function shareExpense() {
        const text = getShareText();
        if (!text) return;
        if (navigator.share) {
            navigator.share({ title: "Farm Expense", text: text }).catch(function () {});
            return;
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
                if (shareButton) shareButton.textContent = "Copied";
            }).catch(openWhatsAppShare);
            return;
        }
        openWhatsAppShare();
    }

    if (shareOverlay && savedExpense) {
        document.body.style.overflow = "hidden";
        if (shareButton) {
            shareButton.addEventListener("click", function (event) {
                event.preventDefault();
                shareExpense();
            });
        }
        if (whatsappButton) {
            whatsappButton.addEventListener("click", function (event) {
                event.preventDefault();
                openWhatsAppShare();
            });
        }
        if (shareCloseButton) {
            shareCloseButton.addEventListener("click", function (event) {
                event.preventDefault();
                closeShareOverlay();
            });
        }
        shareOverlay.addEventListener("click", function (event) {
            if (event.target === shareOverlay) closeShareOverlay();
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeShareOverlay();
        });
    }
});
