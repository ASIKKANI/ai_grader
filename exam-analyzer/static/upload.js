document.getElementById("uploadForm").addEventListener("submit", function() {
  const btn = this.querySelector("button");
  btn.disabled = true;
  btn.textContent = "Analyzing...";
});
