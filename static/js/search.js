/*
===========================================================
 MusicCenter
-----------------------------------------------------------
 Search suggestions dropdown

 Version : 0.2
===========================================================
*/

class MusicSearch {

    constructor() {

        this.inputs = Array.from(
            document.querySelectorAll("#search-input, #global-search")
        );

        this.timer = null;
        this.box = null;

        this.bind();
    }

    bind() {
        this.inputs.forEach((input) => {
            input.addEventListener("input", () => this.changed(input.value));
            input.addEventListener("focus", () => {
                if (input.value.trim().length >= 2) {
                    this.changed(input.value);
                }
            });
        });

        document.addEventListener("click", (event) => {
            if (this.box && !this.box.contains(event.target) && !this.inputs.includes(event.target)) {
                this.hide();
            }
        });
    }

    changed(value) {
        clearTimeout(this.timer);

        if (value.trim().length < 2) {
            this.hide();
            return;
        }

        this.timer = setTimeout(() => this.search(value.trim()), 300);
    }

    async search(query) {
        const data = await Api.suggestions(query);

        if (!data || !data.success) {
            return;
        }

        this.showSuggestions(data.items || []);
    }

    ensureBox() {
        if (this.box) {
            return this.box;
        }

        this.box = document.createElement("div");
        this.box.id = "search-suggestions";
        this.box.className = "search-suggestions";
        document.body.appendChild(this.box);

        return this.box;
    }

    hide() {
        if (this.box) {
            this.box.remove();
            this.box = null;
        }
    }

    showSuggestions(items) {
        if (items.length === 0) {
            this.hide();
            return;
        }

        const box = this.ensureBox();
        box.innerHTML = "";

        const labels = { artist: "исполнитель", album: "альбом", track: "трек" };

        items.forEach((item) => {
            const element = document.createElement("div");
            element.className = "suggestion-item";

            element.innerHTML = `
                <div class="suggestion-type">${labels[item.type] || item.type}</div>
                <div>
                    <strong>${item.title}</strong>
                    ${item.artist ? `<small>${item.artist}</small>` : ""}
                </div>
            `;

            element.addEventListener("click", async () => {
                if (item.type === "artist") {
                    window.location = `/artists/${item.id}`;
                } else if (item.type === "album") {
                    window.location = `/albums/${item.id}`;
                } else if (item.type === "track") {
                    const res = await Api.play({ kind: "track", id: item.id });

                    if (res && res.success && window.Toast) {
                        window.Toast.show(`Играет: ${item.title}`);
                    }

                    this.hide();
                }
            });

            box.appendChild(element);
        });
    }
}

const musicSearch = new MusicSearch();
