document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("generator-form");
    const imageInput = document.getElementById("image-upload");
    const loadingText = document.getElementById("loading-text");
    const generatedImage = document.getElementById("generated-image");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!imageInput.files.length) {
            alert("Please upload an image first.");
            return;
        }

        loadingText.style.display = "block";
        generatedImage.style.display = "none";

        const formData = new FormData();
        formData.append("file", imageInput.files[0]);

        try {
            const response = await fetch("/update", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            loadingText.style.display = "none";
            
            generatedImage.src = result.image_url || URL.createObjectURL(imageInput.files[0]);
            generatedImage.style.display = "block";
            
        } catch (error) {
            console.error("Error during image processing:", error);
            loadingText.style.display = "none";
            alert("An error occurred while processing your image. Please try again.");
        }
    });
});