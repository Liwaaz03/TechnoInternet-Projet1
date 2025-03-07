document.addEventListener("DOMContentLoaded", function () {
    const table = document.querySelector("table");
    const images = [...document.querySelectorAll("table a")].map(a => a.href);
    const container = document.getElementById("container");

    const galleryBtn = document.getElementById("gallerie");
    const carouselBtn = document.getElementById("carrousell");

    galleryBtn.addEventListener("click", showGallery);
    carouselBtn.addEventListener("click", showCarousel);

    function createBackButton() {
        const backBtn = document.createElement("button");
        backBtn.textContent = "Back";
        backBtn.classList.add("back-btn");
        backBtn.addEventListener("click", function () {
            container.innerHTML = "";
            container.appendChild(galleryBtn);
            container.appendChild(carouselBtn);
            table.style.display = "table";
        });
        return backBtn;
    }

    function showGallery() {
        container.innerHTML = "";
        table.style.display = "none";

        const gallery = document.createElement("div");
        gallery.classList.add("gallery");

        images.forEach(src => {
            const img = document.createElement("img");
            img.src = src;
            img.classList.add("gallery-img");
            gallery.appendChild(img);
        });

        container.appendChild(gallery);
        container.appendChild(createBackButton()); // Back Button UNDER the gallery
    }

    function showCarousel() {
        container.innerHTML = "";
        table.style.display = "none";

        const carousel = document.createElement("div");
        carousel.classList.add("carousel");

        const img = document.createElement("img");
        img.src = images[0];
        img.classList.add("carousel-img");

        let index = 0;

        const prevBtn = document.createElement("button");
        prevBtn.textContent = "Previous";
        prevBtn.addEventListener("click", function () {
            index = (index - 1 + images.length) % images.length;
            img.src = images[index];
        });

        const nextBtn = document.createElement("button");
        nextBtn.textContent = "Next";
        nextBtn.addEventListener("click", function () {
            index = (index + 1) % images.length;
            img.src = images[index];
        });

        // Add Back Button BEFORE Previous Button
        container.appendChild(createBackButton());
        container.appendChild(prevBtn);
        container.appendChild(img);
        container.appendChild(nextBtn);
    }

    // Ajout de la fonctionnalité de popup pour chaque ligne de la table
    const rows = table.querySelectorAll("tr");

    rows.forEach((row, index) => {
        row.addEventListener("mousedown", function (event) {
            // Ignorer la ligne d'en-tête
            if (index === 0) return;

            // Récupérer l'image correspondante
            const imgSrc = images[index - 1]; // Ignorer la ligne d'en-tête

            const popup = document.createElement("div");
            popup.classList.add("popup");
            const img = document.createElement("img");
            img.src = imgSrc;
            popup.appendChild(img);

            document.body.appendChild(popup);

            // Ajouter un écouteur d'événements pour la fin du clic (mouseup)
            document.addEventListener("mouseup", function () {
                if (popup) {
                    document.body.removeChild(popup);
                }
            }, { once: true }); // "once: true" pour s'assurer que l'événement ne se déclenche qu'une seule fois
        });
    });
});