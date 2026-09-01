document.addEventListener("DOMContentLoaded", function () {

    console.log("Goat Milk Voice JS loaded");


    /* =========================================================
       ELEMENTS
    ========================================================= */

    const form =
        document.getElementById("goat-milk-form");

    const goatSelect =
        document.getElementById("id_goat");

    const milkRadios =
        document.querySelectorAll(
            'input[name="milk_weight"]'
        );

    const confirmationPopup =
        document.getElementById(
            "milk-voice-confirmation"
        );

    const voiceText =
        document.getElementById(
            "milk-voice-text"
        );

    const confirmationGoat =
        document.getElementById(
            "milk-confirmation-goat"
        );

    const confirmationMilk =
        document.getElementById(
            "milk-confirmation-value"
        );

    const changeButton =
        document.getElementById(
            "milk-confirmation-cancel"
        );

    const saveButton =
        document.getElementById(
            "milk-confirmation-save"
        );


    /* =========================================================
       CHECK ELEMENTS
    ========================================================= */

    if (!form) {
        console.error("Goat milk form not found");
        return;
    }

    if (!goatSelect) {
        console.error("Goat select not found");
        return;
    }

    if (!confirmationPopup) {
        console.error(
            "Milk confirmation popup not found"
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
       GET SELECTED MILK WEIGHT
    ========================================================= */

    function getSelectedMilk() {

        const selected =
            document.querySelector(
                'input[name="milk_weight"]:checked'
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
                ".milk-quantity-option"
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


        const milk =
            getSelectedMilk();


        /*
         * Both fields are required.
         */

        if (!goat || !milk) {

            return;

        }


        /* =====================================================
           DISPLAY DETAILS
        ===================================================== */

        confirmationGoat.textContent =
            goat.text;


        confirmationMilk.textContent =
            `${milk.text} kg`;


        /* =====================================================
           TAMIL MESSAGE
        ===================================================== */

        const tamilMessage =
            `பால் எடை ${milk.text} கிலோ. சரியா?`;


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
         * User can change goat or milk weight.
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
             * goat and milk weight are selected.
             */

            const milk =
                getSelectedMilk();


            if (this.value && milk) {

                openConfirmation();

            }

        }
    );


    /* =========================================================
       MILK WEIGHT CHANGE
    ========================================================= */

    milkRadios.forEach(
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


                const milk =
                    getSelectedMilk();


                /*
                 * Safety check
                 */

                if (!goat || !milk) {

                    return;

                }


                /* =============================================
                   STOP VOICE
                ============================================= */

                stopVoice();


                /* =============================================
                   HIDE MILK WEIGHT RADIO BUTTONS
                ============================================= */

                const quantityButtons =
                    document.querySelector(
                        ".milk-quantity-buttons"
                    );

                if (quantityButtons) {

                    quantityButtons.style.display =
                        "none";

                }


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
                   SUBMIT VIA AJAX
                   (avoids a full page reload between entries)
                ============================================= */

                const formData =
                    new FormData(form);

                const targetUrl =
                    form.action || window.location.href;

                console.log(
                    "Goat milk save: sending to",
                    targetUrl
                );


                /*
                 * Safety timeout so the button
                 * never gets stuck forever if the
                 * request hangs.
                 */

                const abortController =
                    new AbortController();

                const timeoutId =
                    setTimeout(function () {

                        console.warn(
                            "Goat milk save: request timed out after 10s"
                        );

                        abortController.abort();

                    }, 10000);


                fetch(targetUrl, {

                    method: "POST",

                    body: formData,

                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    },

                    credentials: "same-origin",

                    signal: abortController.signal

                })
                    .then(function (response) {

                        clearTimeout(timeoutId);

                        console.log(
                            "Goat milk save: response status",
                            response.status,
                            response.redirected
                                ? "(redirected to " + response.url + ")"
                                : ""
                        );

                        if (!response.ok) {

                            throw new Error(
                                "Save failed with status " +
                                response.status
                            );

                        }

                        return response
                            .clone()
                            .json()
                            .catch(function () {

                                console.warn(
                                    "Goat milk save: response was not JSON — " +
                                    "the Django view likely still needs the " +
                                    "AJAX/JsonResponse handling added."
                                );

                                return null;

                            });

                    })
                    .then(function (data) {

                        if (data && data.success) {

                            console.log(
                                "Goat milk save: success, resetting form"
                            );

                            resetFormForNextEntry();

                        } else if (data && data.success === false) {

                            console.warn(
                                "Goat milk save: validation failed",
                                data.errors
                            );

                            form.submit();

                        } else {

                            /*
                             * No usable JSON back (backend not
                             * updated yet). Fall back to a
                             * normal submit.
                             */

                            form.submit();

                        }

                    })
                    .catch(function (error) {

                        clearTimeout(timeoutId);

                        console.error(
                            "Goat milk save error:",
                            error
                        );

                        /*
                         * Something went wrong with the AJAX
                         * request itself. Fall back to a
                         * normal submit so the save still
                         * goes through.
                         */

                        form.submit();

                    });

            }
        );

    }


    /* =========================================================
       RESET FORM FOR NEXT ENTRY
    ========================================================= */

    function resetFormForNextEntry() {

        /*
         * Close the popup and stop any voice.
         */

        closeConfirmation();


        /*
         * Reset goat + milk weight selection.
         */

        goatSelect.value =
            "";

        milkRadios.forEach(
            function (radio) {

                radio.checked =
                    false;

            }
        );


        /*
         * Show the radio buttons again.
         */

        const quantityButtons =
            document.querySelector(
                ".milk-quantity-buttons"
            );

        if (quantityButtons) {

            quantityButtons.style.display =
                "";

        }


        /*
         * Re-enable the save button.
         */

        saveButton.disabled =
            false;

        saveButton.innerHTML =
            `
            <i class="bi bi-check-lg"></i>
            Confirm &amp; Save
            `;


        /*
         * Ready for the next goat.
         */

        goatSelect.focus();

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