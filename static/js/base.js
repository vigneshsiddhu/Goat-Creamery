document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const dropdowns = document.querySelectorAll(".menu-dropdown");
    const dropdownButtons = document.querySelectorAll(".menu-dropdown-btn");
    const userButton = document.getElementById("userDropdownBtn");
    const userDropdown = document.getElementById("userDropdown");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");

    function normalizePath(path) {
        if (!path || path === "/") return "/";
        return path.replace(/\/+$/, "");
    }

    function isActivePath(currentPath, linkPath) {
        const current = normalizePath(currentPath);
        const link = normalizePath(linkPath);
        if (!link || link === "#") return false;
        if (current === link) return true;
        return current.startsWith(link + "/");
    }

    function getDirectButton(dropdown) {
        const child = dropdown.firstElementChild;
        if (child && child.classList.contains("menu-dropdown-btn")) {
            return child;
        }
        return null;
    }

    function getDropdownForButton(button) {
        const parent = button.parentElement;
        if (parent && parent.classList.contains("menu-dropdown")) {
            return parent;
        }
        return null;
    }

    function isTopLevelDropdown(dropdown) {
        return dropdown.parentElement && dropdown.parentElement.classList.contains("menu");
    }

    function openAncestors(dropdown) {
        let current = dropdown.parentElement ? dropdown.parentElement.closest(".menu-dropdown") : null;
        while (current) {
            current.classList.add("active");
            const button = getDirectButton(current);
            if (button) button.setAttribute("aria-expanded", "true");
            current = current.parentElement ? current.parentElement.closest(".menu-dropdown") : null;
        }
    }

    function setDropdownState(dropdown, isOpen) {
        if (!dropdown) return;
        dropdown.classList.toggle("active", isOpen);
        const button = getDirectButton(dropdown);
        if (button) {
            button.setAttribute("aria-expanded", isOpen ? "true" : "false");
        }
        if (!isOpen) {
            dropdown.querySelectorAll(".menu-dropdown").forEach(function (nested) {
                nested.classList.remove("active");
                const nestedButton = getDirectButton(nested);
                if (nestedButton) nestedButton.setAttribute("aria-expanded", "false");
            });
        }
    }

    function closeTopLevelDropdowns(except) {
        dropdowns.forEach(function (dropdown) {
            if (!isTopLevelDropdown(dropdown) || dropdown === except) return;
            setDropdownState(dropdown, false);
        });
    }

    function closeAllDropdownsAll() {
        dropdowns.forEach(function (dropdown) {
            if (isTopLevelDropdown(dropdown)) {
                setDropdownState(dropdown, false);
            }
        });
    }

    /* User dropdown */
    if (userButton && userDropdown) {
        userButton.addEventListener("click", function (event) {
            event.stopPropagation();
            const isOpen = !userDropdown.classList.contains("show");
            userDropdown.classList.toggle("show", isOpen);
            userButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
        document.addEventListener("click", function (event) {
            if (!userButton.contains(event.target) && !userDropdown.contains(event.target)) {
                userDropdown.classList.remove("show");
                userButton.setAttribute("aria-expanded", "false");
            }
        });
    }

    /* Mobile sidebar */
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", function (event) {
            event.stopPropagation();
            sidebar.classList.toggle("mobile-open");
        });
    }

    /* Sidebar accordion dropdowns */
    dropdownButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            const dropdown = getDropdownForButton(button);
            if (!dropdown) return;

            const willOpen = !dropdown.classList.contains("active");
            if (isTopLevelDropdown(dropdown)) {
                closeTopLevelDropdowns(dropdown);
            }
            setDropdownState(dropdown, willOpen);
            if (willOpen) {
                openAncestors(dropdown);
            }
        });
    });

    /* Active link + auto-open parent section */
    const currentPath = window.location.pathname;
    let bestActiveMatch = null;
    document.querySelectorAll(".menu a").forEach(function (link) {
        const href = link.getAttribute("href");
        if (!href || href === "#") return;

        try {
            const linkPath = new URL(link.href, window.location.origin).pathname;
            if (!isActivePath(currentPath, linkPath)) return;

            if (!bestActiveMatch || linkPath.length > bestActiveMatch.linkPath.length) {
                bestActiveMatch = {
                    link: link,
                    linkPath: linkPath,
                };
            }
        } catch (error) {
            console.warn("Sidebar link error:", error);
        }
    });
    if (bestActiveMatch) {
        bestActiveMatch.link.classList.add("active");
        let openDropdown = bestActiveMatch.link.closest(".menu-dropdown");
        const ancestors = [];
        while (openDropdown) {
            ancestors.unshift(openDropdown);
            openDropdown = openDropdown.parentElement
                ? openDropdown.parentElement.closest(".menu-dropdown")
                : null;
        }
        ancestors.forEach(function (dropdown) {
            if (isTopLevelDropdown(dropdown)) {
                closeTopLevelDropdowns(dropdown);
            }
            setDropdownState(dropdown, true);
        });
    }

    /* Close dropdowns when clicking page content (not sidebar) */
    document.addEventListener("click", function (event) {
        if (sidebar && sidebar.contains(event.target)) {
            return;
        }
        closeAllDropdownsAll();
    });

    /* Close mobile sidebar after navigation */
    document.querySelectorAll(".menu a").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove("mobile-open");
            }
        });
    });

    /* Escape key */
    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;
        closeAllDropdownsAll();
        if (userDropdown) userDropdown.classList.remove("show");
        if (userButton) userButton.setAttribute("aria-expanded", "false");
        if (sidebar) sidebar.classList.remove("mobile-open");
    });
});
