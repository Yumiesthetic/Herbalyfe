document.addEventListener("DOMContentLoaded", function () {
    const searchConfigs = [
        {
            inputId: "herb-search",
            cardClass: ".herb-card",
            nameSelector: "h3",
            sciSelector: ".scientific-name",
            noResultsId: "no-results-herbs"
        },
        {
            inputId: "illness-search",
            cardClass: ".illness-card",
            nameSelector: "h3",
            sciSelector: null, // illnesses don't have a scientific name
            noResultsId: "no-results-illnesses"
        }
    ];

    // Loop through all possible pages (herbs, illnesses)
    searchConfigs.forEach(cfg => applySearch(cfg));
});


function applySearch(cfg) {
    const input = document.getElementById(cfg.inputId);
    if (!input) return; // If not on this page, skip

    const noResults = document.getElementById(cfg.noResultsId);
    const cards = document.querySelectorAll(cfg.cardClass);

    input.addEventListener("keyup", function () {
        const searchValue = this.value.toLowerCase().trim();
        let visibleCount = 0;

        cards.forEach(card => {
            const nameElem = card.querySelector(cfg.nameSelector);
            const sciElem = cfg.sciSelector ? card.querySelector(cfg.sciSelector) : null;

            const originalName = nameElem.dataset.original || nameElem.textContent;
            const nameLower = originalName.toLowerCase();

            // Save original text if not saved yet
            if (!nameElem.dataset.original) nameElem.dataset.original = originalName;

            let match = nameLower.includes(searchValue);

            // Also check scientific name (only for herbs)
            let originalSci = "";
            let sciLower = "";
            if (sciElem) {
                originalSci = sciElem.dataset.original || sciElem.textContent;
                sciLower = originalSci.toLowerCase();
                if (!sciElem.dataset.original) sciElem.dataset.original = originalSci;

                if (sciLower.includes(searchValue)) match = true;
            }

            if (match) {
                card.style.display = "";
                visibleCount++;

                // Add highlight
                nameElem.innerHTML = highlightMatch(originalName, searchValue);

                if (sciElem) {
                    sciElem.innerHTML = highlightMatch(originalSci, searchValue);
                }

            } else {
                card.style.display = "none";
            }
        });

        // Show "No results found"
        if (noResults) {
            noResults.style.display = (visibleCount === 0 ? "block" : "none");
        }
    });
}

function highlightMatch(text, term) {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, "gi");
    return text.replace(regex, `<span class="highlight">$1</span>`);
}
