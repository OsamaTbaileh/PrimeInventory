function fadeInSection(sectionClass) {
    const section = document.querySelector(sectionClass);
    const sectionPosition = section.getBoundingClientRect().top;
    const screenPosition = window.innerHeight / 1.3;

    if (sectionPosition < screenPosition) {
        section.style.opacity = "1";
        section.style.visibility = "visible";
    }
}

window.addEventListener("scroll", () => {
    fadeInSection(".our-vision-section");
    fadeInSection(".about-us-section");
});