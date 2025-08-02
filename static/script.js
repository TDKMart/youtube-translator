document.getElementById("translateForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const url = document.getElementById("url").value;
    const lang = document.getElementById("target_lang").value;
    const progress = document.getElementById("progress");
    const result = document.getElementById("result");
    progress.textContent = "Processing...";
    result.textContent = "";

    const formData = new FormData();
    formData.append("url", url);
    formData.append("target_lang", lang);

    const res = await fetch("/process", { method: "POST", body: formData });
    const data = await res.json();
    const jobId = data.job_id;

    const interval = setInterval(async () => {
        const res = await fetch(`/result/${jobId}`);
        const status = await res.json();
        if (status.status === "done") {
            clearInterval(interval);
            progress.textContent = "✔️ Video is ready!";
            result.innerHTML = `<a href=\"${status.url}\" download>Download translated video</a>`;
        } else if (status.status === "error") {
            clearInterval(interval);
            progress.textContent = "❌ An error occurred.";
        }
    }, 3000);
});