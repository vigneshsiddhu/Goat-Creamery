document.addEventListener("DOMContentLoaded",function(){
    /* ============================================
       USER DROPDOWN
    ============================================ */
    const userButton=document.getElementById("userDropdownBtn");
    const userDropdown=document.getElementById("userDropdown");
    if(userButton&&userDropdown){
        userButton.addEventListener("click",function(event){
            event.stopPropagation();
            userDropdown.classList.toggle("show");
            const isOpen=userDropdown.classList.contains("show");
            userButton.setAttribute("aria-expanded",isOpen);
        });
        document.addEventListener("click",function(event){
            if(!userButton.contains(event.target)&&!userDropdown.contains(event.target)){
                userDropdown.classList.remove("show");
                userButton.setAttribute("aria-expanded","false");
            }
        });
    }

    /* ============================================
       MOBILE SIDEBAR
    ============================================ */
    const mobileMenuBtn=document.getElementById("mobileMenuBtn");
    const sidebar=document.querySelector(".sidebar");
    if(mobileMenuBtn&&sidebar){
        mobileMenuBtn.addEventListener("click",function(event){
            event.stopPropagation();
            sidebar.classList.toggle("mobile-open");
        });
    }

    /* ============================================
       SIDEBAR MENU DROPDOWNS
    ============================================ */
    const dropdowns=document.querySelectorAll(".menu-dropdown");
    const dropdownButtons=document.querySelectorAll(".menu-dropdown-btn");
    dropdownButtons.forEach(function(button){
        button.addEventListener("click",function(event){
            event.preventDefault();
            event.stopPropagation();
            const dropdown=button.closest(".menu-dropdown");
            dropdowns.forEach(function(item){
                if(item!==dropdown){
                    item.classList.remove("active");
                }
            });
            dropdown.classList.toggle("active");
        });
    });

    /* ============================================
       ACTIVE SIDEBAR LINK
    ============================================ */
    const currentPath=window.location.pathname;
    document.querySelectorAll(".menu a").forEach(function(link){
        const href=link.getAttribute("href");
        if(!href||href==="#"||href==="javascript:void(0)"){
            return;
        }
        try{
            const linkPath=new URL(link.href,window.location.origin).pathname;
            if(currentPath===linkPath){
                link.classList.add("active");
                const parentDropdown=link.closest(".menu-dropdown");
                if(parentDropdown){
                    parentDropdown.classList.add("active");
                }
            }
        }catch(error){
            console.warn("Sidebar link error:",error);
        }
    });

    /* ============================================
       CLOSE SIDEBAR DROPDOWNS OUTSIDE
    ============================================ */
    document.addEventListener("click",function(event){
        if(!event.target.closest(".menu-dropdown")){
            dropdowns.forEach(function(dropdown){
                dropdown.classList.remove("active");
            });
        }
    });

    /* ============================================
       KEEP DROPDOWN OPEN INSIDE
    ============================================ */
    document.querySelectorAll(".menu-dropdown-content").forEach(function(content){
        content.addEventListener("click",function(event){
            event.stopPropagation();
        });
    });

    /* ============================================
       CLOSE MOBILE SIDEBAR AFTER LINK CLICK
    ============================================ */
    document.querySelectorAll(".menu a").forEach(function(link){
        link.addEventListener("click",function(){
            if(window.innerWidth<=768&&sidebar){
                sidebar.classList.remove("mobile-open");
            }
        });
    });

    /* ============================================
       ESCAPE KEY
    ============================================ */
    document.addEventListener("keydown",function(event){
        if(event.key==="Escape"){
            dropdowns.forEach(function(dropdown){
                dropdown.classList.remove("active");
            });
            if(userDropdown){
                userDropdown.classList.remove("show");
            }
            if(userButton){
                userButton.setAttribute("aria-expanded","false");
            }
            if(sidebar){
                sidebar.classList.remove("mobile-open");
            }
        }
    });
});