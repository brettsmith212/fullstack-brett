// Function to handle active navbar selection
function activeNavbar() {
	var currentPage = window.location.pathname;
	var aboutLink = document.getElementById("about");
	var blogLink = document.getElementById("blog");

	if (currentPage === "/" || currentPage === "/index.html") {
		if (aboutLink) {
			aboutLink.classList.add("active");
		}
	} else if (currentPage.startsWith("/blog")) {
		if (blogLink) {
			blogLink.classList.add("active");
		}
	}
}

function addCopyButtons() {
	const codeBlocks = document.querySelectorAll("pre");
	codeBlocks.forEach((codeBlock) => {
		if (!codeBlock.querySelector(".copy-button")) {
			// Check if button already exists
			const copyButton = document.createElement("button");
			copyButton.className = "copy-button";
			copyButton.textContent = "Copy";
			codeBlock.style.position = "relative"; // Ensure positioning context
			codeBlock.appendChild(copyButton);

			copyButton.addEventListener("click", () => {
				// Create a temporary element to hold the text content
				const tempElement = document.createElement("div");
				tempElement.innerHTML = codeBlock.innerHTML;

				// Remove the copy button from the temporary element
				const tempButton = tempElement.querySelector(".copy-button");
				if (tempButton) {
					tempButton.remove();
				}

				// Get the text content without the button
				const code = tempElement.textContent.trim();

				navigator.clipboard.writeText(code).then(
					() => {
						copyButton.textContent = "Copied!";
						setTimeout(() => {
							copyButton.textContent = "Copy";
						}, 2000);
					},
					(err) => {
						console.error("Failed to copy: ", err);
						copyButton.textContent = "Failed to copy";
					},
				);
			});
		}
	});
}

document.addEventListener("DOMContentLoaded", function () {
	document.querySelector(".content").classList.add("loaded");
	activeNavbar();
	addCopyButtons();
});
