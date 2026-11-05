document.addEventListener("DOMContentLoaded", function () {

    console.log("Farm Expense Voice JS loaded");

    // =====================================================
    // ELEMENTS
    // =====================================================

    const startBtn = document.getElementById("voice-start-btn");
    const stopBtn = document.getElementById("voice-stop-btn");

    const statusBox = document.getElementById("voice-status");
    const resultBox = document.getElementById("voice-result");
    const errorBox = document.getElementById("voice-error");

    const confirmationBox =
        document.getElementById("voice-confirmation");

    const confirmationText =
        document.getElementById("voice-confirmation-text");

    const yesBtn =
        document.getElementById("voice-yes-btn");

    const noBtn =
        document.getElementById("voice-no-btn");

    const form =
        document.getElementById("farm-expense-form");

    const categoryField =
        document.getElementById("id_category");

    const amountField =
        document.getElementById("id_amount");

    if (amountField) {
        amountField.setAttribute("step", "1");
        amountField.setAttribute("min", "1");
        amountField.setAttribute("placeholder", "5000");
        amountField.setAttribute("inputmode", "numeric");
        amountField.addEventListener("input", function () {
            amountField.value = amountField.value.replace(/[^\d]/g, "");
        });
        if (amountField.value) {
            amountField.value = amountField.value.replace(/[^\d]/g, "");
        }
    }

    const commentField =
        document.getElementById("id_comment");


    // =====================================================
    // BROWSER SUPPORT
    // =====================================================

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    const speechSynthesis =
        window.speechSynthesis;


    if (!SpeechRecognition) {

        statusBox.innerText =
            "Voice recognition is not supported. Please use Google Chrome.";

        startBtn.disabled = true;

        return;
    }


    // =====================================================
    // VARIABLES
    // =====================================================

    let recognition = null;

    let mode = null;

    let isListening = false;

    let waitingForConfirmation = false;

    let submitting = false;

    let currentCategory = "";

    let currentAmount = "";

    let currentComment = "";


    // =====================================================
    // CREATE RECOGNITION
    // =====================================================

    function createRecognition(language) {

        const r = new SpeechRecognition();

        r.lang = language;

        r.continuous = false;

        r.interimResults = false;

        r.maxAlternatives = 5;


        r.onstart = function () {

            isListening = true;

            console.log(
                "Speech recognition started:",
                language
            );
        };


        r.onresult = function (event) {

            isListening = false;

            const text =
                event.results[0][0]
                    .transcript
                    .trim();


            console.log(
                "Recognized:",
                text
            );


            if (resultBox) {

                resultBox.value = text;
            }


            if (mode === "expense") {

                processExpense(text);
            }


            if (mode === "confirmation") {

                processConfirmation(text);
            }
        };


        r.onerror = function (event) {

            isListening = false;


            console.log(
                "Speech error:",
                event.error
            );


            /*
             * IMPORTANT:
             *
             * "aborted" is normally a browser
             * interruption, not a real failure.
             */

            if (event.error === "aborted") {

                console.log(
                    "Recognition aborted - ignored."
                );

                return;
            }


            if (event.error === "no-speech") {

                statusBox.innerText =
                    "No speech detected. Please try again.";

                resetButtons();

                return;
            }


            if (event.error === "not-allowed") {

                statusBox.innerText =
                    "Microphone permission is blocked.";

                resetButtons();

                return;
            }


            statusBox.innerText =
                "Voice recognition error: " +
                event.error;


            resetButtons();
        };


        r.onend = function () {

            isListening = false;

            console.log(
                "Speech recognition ended."
            );
        };


        return r;
    }


    // =====================================================
    // START EXPENSE
    // =====================================================

    startBtn.addEventListener(
        "click",
        function () {

            startExpenseListening();

        }
    );


    function startExpenseListening() {

        if (submitting) {
            return;
        }


        if (speechSynthesis) {

            speechSynthesis.cancel();
        }


        waitingForConfirmation = false;

        mode = "expense";


        currentCategory = "";

        currentAmount = "";

        currentComment = "";


        confirmationBox.style.display =
            "none";


        errorBox.style.display =
            "none";


        resultBox.value = "";


        statusBox.innerText =
            "🎤 Listening... Please say expense category and amount.";


        startBtn.style.display =
            "none";


        stopBtn.style.display =
            "inline-flex";


        /*
         * Create a NEW recognition object.
         *
         * This avoids the aborted problem caused
         * by reusing a stopped recognition object.
         */

        recognition =
            createRecognition("en-IN");


        try {

            recognition.start();

        }
        catch (error) {

            console.log(
                "Recognition start error:",
                error
            );

            resetButtons();
        }
    }


    // =====================================================
    // PROCESS EXPENSE
    // =====================================================

    function processExpense(text) {

        console.log(
            "Processing expense:",
            text
        );


        // -------------------------------------------------
        // AMOUNT
        // -------------------------------------------------

        const amount =
            extractAmount(text);


        console.log(
            "Amount:",
            amount
        );


        if (!amount) {

            statusBox.innerText =
                "Amount not detected.";


            speakTamil(
                "Amount கிடைக்கவில்லை. Medicine 1500 என்று சொல்லுங்கள்."
            );


            resetButtons();

            return;
        }


        currentAmount =
            amount;


        // -------------------------------------------------
        // CATEGORY
        // -------------------------------------------------

        const category =
            extractCategory(text);


        console.log(
            "Category:",
            category
        );


        if (!category) {

            statusBox.innerText =
                "Category not detected.";


            speakTamil(
                "Category கிடைக்கவில்லை. மீண்டும் சொல்லுங்கள்."
            );


            resetButtons();

            return;
        }


        currentCategory =
            category;


        // -------------------------------------------------
        // SET CATEGORY
        // -------------------------------------------------

        if (!setCategory(category)) {

            statusBox.innerText =
                category +
                " category is not available.";


            speakTamil(
                category +
                " category form-ல் இல்லை."
            );


            resetButtons();

            return;
        }


        // -------------------------------------------------
        // SET AMOUNT
        // -------------------------------------------------

        amountField.value =
            currentAmount;


        amountField.dispatchEvent(
            new Event(
                "input",
                { bubbles: true }
            )
        );


        amountField.dispatchEvent(
            new Event(
                "change",
                { bubbles: true }
            )
        );


        // -------------------------------------------------
        // COMMENT
        // -------------------------------------------------

        currentComment =
            extractComment(
                text,
                currentAmount,
                currentCategory
            );


        if (commentField) {

            commentField.value =
                currentComment;
        }


        console.log(
            "Final category:",
            currentCategory
        );


        console.log(
            "Final amount:",
            currentAmount
        );


        // -------------------------------------------------
        // CONFIRMATION
        // -------------------------------------------------

        askConfirmation();
    }


    // =====================================================
    // EXTRACT AMOUNT
    // =====================================================

    function extractAmount(text) {

        /*
         * Handles:
         *
         * Medicine 1500
         * Medicine ₹1500
         * Medicine rs 1500
         * Feed 2000 rupees
         */

        const match =
            text.match(
                /(?:₹|rs\.?|rupees?)?\s*(\d+)/i
            );


        if (match) {

            return String(parseInt(match[1], 10));
        }


        /*
         * English number words
         */

        const words =
            text
                .toLowerCase()
                .replace(/[,.!?]/g, "")
                .split(/\s+/);


        const numbers = {

            one: 1,
            two: 2,
            three: 3,
            four: 4,
            five: 5,
            six: 6,
            seven: 7,
            eight: 8,
            nine: 9,

            ten: 10,

            twenty: 20,
            thirty: 30,
            forty: 40,
            fifty: 50,
            sixty: 60,
            seventy: 70,
            eighty: 80,
            ninety: 90
        };


        let total = 0;

        let current = 0;

        let found = false;


        words.forEach(
            function (word) {

                if (
                    numbers[word] !== undefined
                ) {

                    current +=
                        numbers[word];

                    found = true;
                }


                else if (
                    word === "hundred"
                ) {

                    if (current === 0) {

                        current = 1;
                    }

                    current *= 100;

                    found = true;
                }


                else if (
                    word === "thousand"
                ) {

                    if (current === 0) {

                        current = 1;
                    }

                    total +=
                        current * 1000;

                    current = 0;

                    found = true;
                }


                else if (
                    word === "lakh" ||
                    word === "lakhs"
                ) {

                    if (current === 0) {

                        current = 1;
                    }

                    total +=
                        current * 100000;

                    current = 0;

                    found = true;
                }

            }
        );


        total += current;


        if (
            found &&
            total > 0
        ) {

            return String(total);
        }


        return null;
    }


    // =====================================================
    // EXTRACT CATEGORY
    // =====================================================

    function extractCategory(text) {

        const lower =
            text.toLowerCase();


        if (
            lower.includes("medicine") ||
            lower.includes("medicines") ||
            lower.includes("medical")
        ) {

            return "Medicine";
        }


        if (
            lower.includes("feed") ||
            lower.includes("fodder")
        ) {

            return "Feed";
        }


        if (
            lower.includes("labour") ||
            lower.includes("labor") ||
            lower.includes("worker")
        ) {

            return "Labour";
        }


        if (
            lower.includes("electricity") ||
            lower.includes("current") ||
            lower.includes("power")
        ) {

            return "Electricity";
        }


        if (
            lower.includes("transport") ||
            lower.includes("transportation")
        ) {

            return "Transport";
        }


        if (
            lower.includes("maintenance") ||
            lower.includes("repair")
        ) {

            return "Maintenance";
        }


        /*
         * Check Django select options.
         */

        if (categoryField) {

            const options =
                Array.from(
                    categoryField.options
                );


            for (
                const option of options
            ) {

                const optionText =
                    option.text
                        .trim()
                        .toLowerCase();


                const optionValue =
                    option.value
                        .trim()
                        .toLowerCase();


                if (
                    lower.includes(optionText) ||
                    lower.includes(optionValue)
                ) {

                    return option.text.trim();
                }
            }
        }


        return null;
    }


    // =====================================================
    // SET CATEGORY
    // =====================================================

    function setCategory(category) {

        if (!categoryField) {

            return false;
        }


        const wanted =
            category
                .trim()
                .toLowerCase();


        const option =
            Array.from(
                categoryField.options
            ).find(
                function (option) {

                    return (
                        option.value
                            .trim()
                            .toLowerCase() === wanted ||

                        option.text
                            .trim()
                            .toLowerCase() === wanted
                    );
                }
            );


        if (!option) {

            return false;
        }


        categoryField.value =
            option.value;


        categoryField.dispatchEvent(
            new Event(
                "change",
                { bubbles: true }
            )
        );


        return true;
    }


    // =====================================================
    // COMMENT
    // =====================================================

    function extractComment(
        text,
        amount,
        category
    ) {

        let comment = text;


        comment =
            comment.replace(
                amount,
                ""
            );


        comment =
            comment.replace(
                new RegExp(
                    category,
                    "gi"
                ),
                ""
            );


        comment =
            comment
                .replace(
                    /rupees?/gi,
                    ""
                )
                .replace(
                    /rs\.?/gi,
                    ""
                )
                .replace(
                    /expense/gi,
                    ""
                )
                .trim();


        return comment.length >= 2
            ? comment
            : "";
    }


    // =====================================================
    // ASK CONFIRMATION
    // =====================================================

    function askConfirmation() {

        waitingForConfirmation =
            true;


        mode =
            "confirmation";


        confirmationBox.style.display =
            "block";


        confirmationText.innerText =
            `${currentCategory} - ₹${currentAmount}`;


        statusBox.innerText =
            "சரி அல்லது தவறு என்று சொல்லுங்கள்.";


        /*
         * First speak.
         * Only AFTER speech ends we start
         * the microphone.
         */

        speakTamil(
            `${currentCategory}, ${currentAmount} ரூபாய். சரியா? சரி அல்லது தவறு என்று சொல்லுங்கள்.`,
            function () {

                setTimeout(
                    function () {

                        if (
                            waitingForConfirmation
                        ) {

                            startConfirmation();
                        }

                    },
                    800
                );
            }
        );
    }


    // =====================================================
    // TAMIL SPEECH
    // =====================================================

    function speakTamil(
        text,
        callback
    ) {

        console.log(
            "Speaking Tamil:",
            text
        );


        if (!speechSynthesis) {

            if (callback) {
                callback();
            }

            return;
        }


        speechSynthesis.cancel();


        const utterance =
            new SpeechSynthesisUtterance(
                text
            );


        utterance.lang =
            "ta-IN";


        utterance.rate =
            0.8;


        utterance.pitch =
            1;


        utterance.volume =
            1;


        utterance.onend =
            function () {

                if (callback) {

                    callback();
                }
            };


        utterance.onerror =
            function () {

                if (callback) {

                    callback();
                }
            };


        speechSynthesis.speak(
            utterance
        );
    }


    // =====================================================
    // START CONFIRMATION
    // =====================================================

    function startConfirmation() {

        if (
            !waitingForConfirmation
        ) {

            return;
        }


        console.log(
            "Starting Tamil confirmation recognition"
        );


        mode =
            "confirmation";


        statusBox.innerText =
            "🎤 சரி அல்லது தவறு என்று சொல்லுங்கள்.";


        /*
         * New object.
         */

        recognition =
            createRecognition("ta-IN");


        try {

            recognition.start();

        }
        catch (error) {

            console.log(
                "Confirmation start error:",
                error
            );


            /*
             * Browser sometimes needs a
             * short delay after speech synthesis.
             */

            setTimeout(
                function () {

                    if (
                        waitingForConfirmation
                    ) {

                        startConfirmation();
                    }

                },
                1000
            );
        }
    }


    // =====================================================
    // CONFIRMATION
    // =====================================================

    function processConfirmation(answer) {

        const value =
            answer
                .toLowerCase()
                .replace(
                    /[.,!?]/g,
                    ""
                )
                .trim();


        console.log(
            "Confirmation answer:",
            value
        );


        // -------------------------------------------------
        // NO
        // -------------------------------------------------

        if (isNo(value)) {

            waitingForConfirmation =
                false;


            confirmationBox.style.display =
                "none";


            statusBox.innerText =
                "சரி. மீண்டும் expense சொல்லுங்கள்.";


            speakTamil(
                "சரி. மீண்டும் expense details சொல்லுங்கள்."
            );


            resetButtons();


            return;
        }


        // -------------------------------------------------
        // YES
        // -------------------------------------------------

        if (isYes(value)) {

            waitingForConfirmation =
                false;


            confirmationBox.style.display =
                "none";


            statusBox.innerText =
                "சரி. Expense save செய்கிறேன்.";


            speakTamil(
                "சரி. Expense save செய்கிறேன்.",
                function () {

                    setTimeout(
                        function () {

                            submitExpense();

                        },
                        500
                    );
                }
            );


            return;
        }


        // -------------------------------------------------
        // UNKNOWN
        // -------------------------------------------------

        statusBox.innerText =
            "சரி அல்லது தவறு என்று சொல்லுங்கள்.";


        speakTamil(
            "சரி அல்லது தவறு என்று சொல்லுங்கள்.",
            function () {

                setTimeout(
                    function () {

                        if (
                            waitingForConfirmation
                        ) {

                            startConfirmation();
                        }

                    },
                    800
                );
            }
        );
    }


    // =====================================================
    // YES
    // =====================================================

    function isYes(value) {

        const words = [

            "ஆம்",
            "ஆமாம்",
            "ஆமா",
            "சரி",
            "சரிங்க",
            "சரிதான்",
            "சரியே",

            "yes",
            "yeah",
            "yep",
            "correct",
            "right",
            "ok",
            "okay",
            "confirm",
            "confirmed"
        ];


        return words.some(
            function (word) {

                return value.includes(
                    word
                );
            }
        );
    }


    // =====================================================
    // NO
    // =====================================================

    function isNo(value) {

        const words = [

            "இல்லை",
            "இல்ல",
            "வேண்டாம்",
            "தவறு",
            "தப்பு",
            "சரியில்லை",

            "no",
            "wrong",
            "incorrect",
            "not correct",
            "cancel"
        ];


        return words.some(
            function (word) {

                return value.includes(
                    word
                );
            }
        );
    }


    // =====================================================
    // SUBMIT
    // =====================================================

    function submitExpense() {

        if (submitting) {

            return;
        }


        submitting =
            true;


        /*
         * Final safety assignment.
         */

        setCategory(
            currentCategory
        );


        amountField.value =
            currentAmount;


        if (commentField) {

            commentField.value =
                currentComment;
        }


        console.log(
            "Submitting:",
            currentCategory,
            currentAmount,
            currentComment
        );


        if (!form) {

            console.error(
                "Farm expense form not found"
            );

            submitting =
                false;

            return;
        }


        /*
         * requestSubmit()
         * triggers normal Django form submission.
         */

        if (
            typeof form.requestSubmit ===
            "function"
        ) {

            form.requestSubmit();

        }
        else {

            form.submit();
        }
    }


    // =====================================================
    // STOP
    // =====================================================

    function stopAllRecognition() {

        waitingForConfirmation =
            false;


        if (recognition) {

            try {

                recognition.abort();

            }
            catch (error) {

                console.log(error);
            }
        }


        recognition =
            null;


        isListening =
            false;
    }


    // =====================================================
    // STOP BUTTON
    // =====================================================

    stopBtn.addEventListener(
        "click",
        function () {

            stopAllRecognition();


            if (speechSynthesis) {

                speechSynthesis.cancel();
            }


            confirmationBox.style.display =
                "none";


            statusBox.innerText =
                "Voice stopped.";


            resetButtons();
        }
    );


    // =====================================================
    // YES BUTTON
    // =====================================================

    yesBtn.addEventListener(
        "click",
        function () {

            if (
                !waitingForConfirmation
            ) {

                return;
            }


            processConfirmation(
                "சரி"
            );
        }
    );


    // =====================================================
    // NO BUTTON
    // =====================================================

    noBtn.addEventListener(
        "click",
        function () {

            if (
                !waitingForConfirmation
            ) {

                return;
            }


            processConfirmation(
                "தவறு"
            );
        }
    );


    // =====================================================
    // RESET
    // =====================================================

    function resetButtons() {

        startBtn.style.display =
            "inline-flex";


        stopBtn.style.display =
            "none";
    }


    // =====================================================
    // INITIAL
    // =====================================================

    resetButtons();


    confirmationBox.style.display =
        "none";


    console.log(
        "Farm Expense Voice System READY"
    );

});