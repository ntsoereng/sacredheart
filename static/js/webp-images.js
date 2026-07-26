document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("img[data-webp-src]").forEach((image) => {
        const webpUrl = image.dataset.webpSrc;
        if (!webpUrl) return;

        const candidate = new Image();
        candidate.onload = () => {
            image.src = webpUrl;
        };
        candidate.onerror = () => {
            // Keep the working original image already in src.
        };
        candidate.src = webpUrl;
    });
});
