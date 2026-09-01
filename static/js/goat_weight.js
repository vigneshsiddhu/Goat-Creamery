document.addEventListener("DOMContentLoaded", function () {

    console.log("Goat Weight Voice JS loaded");


    /* =========================================================
       ELEMENTS
    ========================================================= */

    const form =
        document.getElementById("goat-weight-form");

    const goatSelect =
        document.getElementById("id_goat");

    const weightRadios =
        document.querySelectorAll(
            'input[name="weight"]'
        );

    const confirmationPopup =
        document.getElementById(
            "weight-voice-confirmation"
        );

    const voiceText =
        document.getElementById(
            "weight-voice-text"
        );

    const confirmationGoat =
        document.getElementById(
            "weight-confirmation-goat"
        );

    const confirmationWeight =
        document.getElementById(
            "weight-confirmation-value"
        );

    const changeButton =
        document.getElementById(
            "weight-confirmation-cancel"
        );

    const saveButton =
        document.getElementById(
            "weight-confirmation-save"
        );


    /* =========================================================
       CHECK ELEMENTS
    ========================================================= */

    if (!form) {
        console.error("Goat weight form not found");
        return;
    }

    if (!goatSelect) {
        console.error("Goat select not found");
        return;
    }

    if (!confirmationPopup) {
        console.error(
            "Weight confirmation popup not found"
        );
        return;
    }


    /* =========================================================
       TAMIL VOICE
    ========================================================= */

    function speakTamil(text) {

        if (!("speechSynthesis" in window)) {

            console.warn(
                "Speech synthesis is not supported"
            );

            return;
        }


        // Stop previous speech

        window.speechSynthesis.cancel();


        const utterance =
            new SpeechSynthesisUtterance(text);


        // Tamil India

        utterance.lang = "ta-IN";

        utterance.rate = 0.9;

        utterance.pitch = 1;

        utterance.volume = 1;


        window.speechSynthesis.speak(
            utterance
        );
    }


    /* =========================================================
       STOP VOICE
    ========================================================= */

    function stopVoice() {

        if ("speechSynthesis" in window) {

            window.speechSynthesis.cancel();

        }
    }


    /* =========================================================
       GET SELECTED GOAT
    ========================================================= */

    function getSelectedGoat() {

        if (
            !goatSelect.value ||
            goatSelect.selectedIndex < 0
        ) {

            return null;

        }


        const option =
            goatSelect.options[
                goatSelect.selectedIndex
            ];


        return {

            value: goatSelect.value,

            text: option.textContent.trim()

        };
    }


    /* =========================================================
       GET SELECTED WEIGHT
    ========================================================= */

    function getSelectedWeight() {

        const selected =
            document.querySelector(
                'input[name="weight"]:checked'
            );


        if (!selected) {

            return null;

        }


        let labelText = "";


        /*
         * Try to get the text from the label.
         */

        const label =
            selected.closest(
                ".weight-quantity-option"
            );


        if (label) {

            const span =
                label.querySelector("span");


            if (span) {

                labelText =
                    span.textContent.trim();

            }

        }


        /*
         * Fallback to radio value
         */

        if (!labelText) {

            labelText =
                selected.value;

        }


        /*
         * Remove kg if already present.
         */

        labelText =
            labelText
                .replace(/\s*kg\s*/gi, "")
                .trim();


        return {

            value: selected.value,

            text: labelText

        };

    }


    /* =========================================================
       OPEN CONFIRMATION POPUP
    ========================================================= */

    function openConfirmation() {

        const goat =
            getSelectedGoat();


        const weight =
            getSelectedWeight();


        /*
         * Both fields are required.
         */

        if (!goat || !weight) {

            return;

        }


        /* =====================================================
           DISPLAY DETAILS
        ===================================================== */

        confirmationGoat.textContent =
            goat.text;


        confirmationWeight.textContent =
            `${weight.text} kg`;


        /* =====================================================
           TAMIL MESSAGE
        ===================================================== */

        const tamilMessage =
            `எடை ${weight.text} கிலோ. சரியா?`;


        voiceText.textContent =
            tamilMessage;


        /* =====================================================
           SHOW POPUP
        ===================================================== */

        confirmationPopup.style.display =
            "flex";


        /*
         * Prevent background scrolling
         */

        document.body.style.overflow =
            "hidden";


        /* =====================================================
           SPEAK TAMIL
        ===================================================== */

        setTimeout(function () {

            speakTamil(tamilMessage);

        }, 200);

    }


    /* =========================================================
       CLOSE CONFIRMATION POPUP
    ========================================================= */

    function closeConfirmation() {

        stopVoice();


        confirmationPopup.style.display =
            "none";


        /*
         * Restore scrolling
         */

        document.body.style.overflow =
            "";


        /*
         * Do NOT clear the selected values.
         *
         * User can change goat or weight.
         */

    }


    /* =========================================================
       GOAT CHANGE
    ========================================================= */

    goatSelect.addEventListener(
        "change",
        function () {

            /*
             * Only open popup when both
             * goat and weight are selected.
             */

            const weight =
                getSelectedWeight();


            if (this.value && weight) {

                openConfirmation();

            }

        }
    );


    /* =========================================================
       WEIGHT CHANGE
    ========================================================= */

    weightRadios.forEach(
        function (radio) {

            radio.addEventListener(
                "change",
                function () {

                    /*
                     * Only open when goat
                     * is selected.
                     */

                    if (goatSelect.value) {

                        openConfirmation();

                    }

                }
            );

        }
    );


    /* =========================================================
       CHANGE BUTTON
    ========================================================= */

    if (changeButton) {

        changeButton.addEventListener(
            "click",
            function () {

                closeConfirmation();


                /*
                 * Focus goat select so user
                 * can change the selection.
                 */

                goatSelect.focus();

            }
        );

    }


    /* =========================================================
       CONFIRM & SAVE
    ========================================================= */

    if (saveButton) {

        saveButton.addEventListener(
            "click",
            function () {

                const goat =
                    getSelectedGoat();


                const weight =
                    getSelectedWeight();


                /*
                 * Safety check
                 */

                if (!goat || !weight) {

                    return;

                }


                /* =============================================
                   STOP VOICE
                ============================================= */

                stopVoice();


                /* =============================================
                   DISABLE BUTTON
                ============================================= */

                saveButton.disabled =
                    true;


                saveButton.innerHTML =
                    `
                    <i class="bi bi-hourglass-split"></i>
                    Saving...
                    `;


                /* =============================================
                   SUBMIT FORM
                ============================================= */

                form.submit();

            }
        );

    }


    /* =========================================================
       PREVENT ENTER FROM SUBMITTING DIRECTLY
       ========================================================= */

    form.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                confirmationPopup.style.display !== "flex"
            ) {

                event.preventDefault();

            }

        }
    );


    /* =========================================================
       CLICK OUTSIDE POPUP
       ========================================================= */

    confirmationPopup.addEventListener(
        "click",
        function (event) {

            /*
             * Do not close when clicking
             * inside popup.
             */

            if (
                event.target ===
                confirmationPopup
            ) {

                closeConfirmation();

            }

        }
    );


    /* =========================================================
       ESC KEY
    ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                confirmationPopup.style.display === "flex"
            ) {

                closeConfirmation();

            }

        }
    );


    /* =========================================================
       CLEANUP WHEN LEAVING PAGE
    ========================================================= */

    window.addEventListener(
        "beforeunload",
        function () {

            stopVoice();

        }
    );


});