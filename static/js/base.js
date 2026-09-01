document.addEventListener("DOMContentLoaded", function () {

    /* ============================================
       USER DROPDOWN
    ============================================ */

    const userButton = document.getElementById("userDropdownBtn");
    const userDropdown = document.getElementById("userDropdown");

    if (userButton && userDropdown) {

        userButton.addEventListener("click", function (event) {

            event.stopPropagation();

            userDropdown.classList.toggle("show");

            const isOpen =
                userDropdown.classList.contains("show");

            userButton.setAttribute(
                "aria-expanded",
                isOpen
            );
        });


        /* Close when clicking outside */

        document.addEventListener("click", function (event) {

            if (
                !userButton.contains(event.target) &&
                !userDropdown.contains(event.target)
            ) {

                userDropdown.classList.remove("show");

                userButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        });
    }


    /* ============================================
       MOBILE SIDEBAR
    ============================================ */

    const mobileMenuBtn =
        document.getElementById("mobileMenuBtn");

    const sidebar =
        document.querySelector(".sidebar");


    if (mobileMenuBtn && sidebar) {

        mobileMenuBtn.addEventListener("click", function () {

            sidebar.classList.toggle("mobile-open");

        });
    }

});