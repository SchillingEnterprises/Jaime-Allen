document.querySelectorAll("[data-current-year]").forEach((element) => {
    const currentYear = String(new Date().getFullYear());
    element.textContent = currentYear;

    if (element.tagName === "TIME") {
        element.setAttribute("datetime", currentYear);
    }
});
