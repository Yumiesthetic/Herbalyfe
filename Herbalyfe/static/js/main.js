// Image Overlay Functionality (for both herbs and illnesses)
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("image-overlay");
  const overlayImage = document.getElementById("overlay-image");

  // Herb image
  const herbImage = document.getElementById("herb-image");
  if (herbImage && overlay && overlayImage) {
    herbImage.addEventListener("click", () => {
      overlayImage.src = herbImage.src;
      overlay.style.display = "flex";
    });
  }

  // Illness image
  const illnessImage = document.getElementById("illness-image");
  if (illnessImage && overlay && overlayImage) {
    illnessImage.addEventListener("click", () => {
      overlayImage.src = illnessImage.src;
      overlay.style.display = "flex";
    });
  }

  // Home logo image
  const homeLogo = document.getElementById("home-logo");
  if (homeLogo && overlay && overlayImage) {
    homeLogo.addEventListener("click", () => {
      overlayImage.src = homeLogo.src;
      overlay.style.display = "flex";
    });
  }

  // Close overlay when clicking outside the image
  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.style.display = "none";
      }
    });
  }
});

// Logout confirmation
document.addEventListener("DOMContentLoaded", () => {
  const logoutLink = document.querySelector(".logout-link");
  if (logoutLink) {
    logoutLink.addEventListener("click", (e) => {
      const confirmed = confirm("Are you sure you want to log out?");
      if (!confirmed) {
        e.preventDefault(); // Cancel logout if user clicks "Cancel"
        }
      });
    }
});
