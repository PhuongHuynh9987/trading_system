tailwind.config = {
        darkMode: "class",
        theme: {
                extend: {
                "colors": {
                        "surface-dim": "#ccdcec",
                        "on-secondary-container": "#3a5470",
                        "surface": "#f7f9ff",
                        "outline-variant": "#a6b3c1",
                        "surface-container-lowest": "#ffffff",
                        "on-primary-fixed": "#353f56",
                        "on-surface-variant": "#54606c",
                        "on-background": "#28343e",
                        "on-secondary": "#f7f9ff",
                        "surface-container": "#e7eff8",
                        "on-secondary-fixed-variant": "#445d7b",
                        "on-error-container": "#752121",
                        "on-tertiary-container": "#4a4f69",
                        "secondary": "#48617e",
                        "error": "#9f403d",
                        "on-primary-fixed-variant": "#515c73",
                        "secondary-container": "#d1e4ff",
                        "primary": "#545e76",
                        "tertiary-fixed": "#dadefe",
                        "on-error": "#fff7f6",
                        "primary-container": "#d7e2ff",
                        "on-tertiary-fixed-variant": "#545873",
                        "tertiary-dim": "#4d526c",
                        "inverse-surface": "#0b0f12",
                        "primary-dim": "#48526a",
                        "surface-container-highest": "#d7e4f2",
                        "on-tertiary": "#faf8ff",
                        "secondary-dim": "#3c5572",
                        "tertiary": "#595e78",
                        "on-surface": "#28343e",
                        "tertiary-container": "#dadefe",
                        "surface-tint": "#545e76",
                        "error-dim": "#4e0309",
                        "tertiary-fixed-dim": "#ccd0ef",
                        "surface-variant": "#d7e4f2",
                        "secondary-fixed": "#d1e4ff",
                        "on-primary-container": "#475269",
                        "on-secondary-fixed": "#27415d",
                        "surface-bright": "#f7f9ff",
                        "background": "#f7f9ff",
                        "inverse-primary": "#d7e2ff",
                        "inverse-on-surface": "#9a9da2",
                        "surface-container-high": "#dfe9f5",
                        "error-container": "#fe8983",
                        "primary-fixed": "#d7e2ff",
                        "surface-container-low": "#eff4fc",
                        "secondary-fixed-dim": "#bdd7f9",
                        "outline": "#6f7c88",
                        "primary-fixed-dim": "#c9d4f0",
                        "on-primary": "#f7f7ff",
                        "on-tertiary-fixed": "#383c55",
                        "success": "#15803d",
                        "success-container": "#dcfce7",
                        "warning": "#a16207",
                        "warning-container": "#fef9c3"
                },
                "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                },
                "fontFamily": {
                        "headline": ["Manrope"],
                        "body": ["Inter"],
                        "label": ["Inter"]
                }
                },
        },
}

function openModal() {
      document.getElementById("myModal").style.display = "block";
    }

    function closeModal() {
      document.getElementById("myModal").style.display = "none";
    }

    // Close when clicking outside
    window.onclick = function(event) {
      let modal = document.getElementById("myModal");
      if (event.target === modal) {
        modal.style.display = "none";
      }
    }
    