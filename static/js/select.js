/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Custom Select

 Native <select> dropdown popups can't be restyled to match
 the glass theme (browser-owned, no CSS access). This
 progressively enhances every <select class="sort-select">
 with a themed button + popup, while keeping the original
 <select> in the DOM as the source of truth - existing
 onchange="" attributes and addEventListener("change", ...)
 wiring elsewhere (albums/artists sort, EQ picker) keep
 working untouched, since option clicks just set .value and
 dispatch a real "change" event on it.

 Version : 0.1
===========================================================
*/

function enhanceSelect(select) {
    if (select.dataset.enhanced) {
        return;
    }

    select.dataset.enhanced = "true";

    const wrapper = document.createElement("div");
    wrapper.className = "csel";

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    select.classList.add("csel-native");

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "sort-select csel-trigger";

    const label = document.createElement("span");
    trigger.appendChild(label);

    const chevron = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    chevron.setAttribute("class", "icon");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", "/static/icons/sprite.svg#chevron-down");
    chevron.appendChild(use);
    trigger.appendChild(chevron);

    const menu = document.createElement("div");
    menu.className = "csel-menu";
    menu.hidden = true;

    const optionButtons = Array.from(select.options).map((option) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "csel-option";
        btn.textContent = option.textContent;
        btn.dataset.value = option.value;

        btn.addEventListener("click", () => {
            select.value = option.value;
            sync();
            select.dispatchEvent(new Event("change", { bubbles: true }));
            close();
        });

        menu.appendChild(btn);
        return btn;
    });

    function sync() {
        const selected = select.options[select.selectedIndex];
        label.textContent = selected ? selected.textContent : "";

        optionButtons.forEach((btn) => {
            btn.classList.toggle("selected", btn.dataset.value === select.value);
        });
    }

    function open() {
        menu.hidden = false;
        wrapper.classList.add("open");
        document.addEventListener("click", onOutsideClick);
    }

    function close() {
        menu.hidden = true;
        wrapper.classList.remove("open");
        document.removeEventListener("click", onOutsideClick);
    }

    function onOutsideClick(event) {
        if (!wrapper.contains(event.target)) {
            close();
        }
    }

    trigger.addEventListener("click", () => {
        if (menu.hidden) {
            open();
        } else {
            close();
        }
    });

    trigger.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            close();
        }
    });

    // Exposed so code that sets select.value directly (e.g. player.js
    // syncing the EQ preset from server state) can refresh the custom UI
    // without dispatching a fake "change" event - that would also re-fire
    // this select's own app-level change handler and send a redundant
    // request for a value that just came from the server.
    select.cselSync = sync;

    wrapper.appendChild(trigger);
    wrapper.appendChild(menu);

    sync();
}

function enhanceAllSelects() {
    document.querySelectorAll("select.sort-select").forEach(enhanceSelect);
}

document.addEventListener("DOMContentLoaded", enhanceAllSelects);

window.enhanceAllSelects = enhanceAllSelects;
