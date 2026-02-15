document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const resultsDiv = document.getElementById("results");
  const loadingDiv = document.getElementById("loading");

  // Clear previous results and show loading
  resultsDiv.innerHTML = "";
  loadingDiv.style.display = "block";

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    // Hide loading indicator
    loadingDiv.style.display = "none";

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Raw response:", result);

    // Error handling logic
    if (result.error) {
      if (result.error.includes("quota")) {
        resultsDiv.innerHTML = `
          <div class="error">
            <h2>API Quota Exceeded</h2>
            <p>We've reached our API usage limit. Please try again later or contact support.</p>
          </div>`;
      } else {
        resultsDiv.innerHTML = `
          <div class="error">
            <h2>Error</h2>
            <p>${result.error}</p>
          </div>`;
      }
      return;
    }

    // Parse logic
    let feedback;
    if (result.raw_content) {
      try {
        feedback = JSON.parse(result.raw_content);
      } catch (e) {
        console.error("Failed to parse raw content:", e);
        resultsDiv.innerHTML = `<div class="error"><h2>Error</h2><p>Failed to parse resume analysis.</p></div>`;
        return;
      }
    } else {
      feedback = result;
    }

    // 1. Create the Top Grid Wrapper (Horizontal Layout)
    const resultsWrapper = document.createElement("div");
    resultsWrapper.id = "results-grid"; 
    resultsDiv.appendChild(resultsWrapper);

    // 2. ATS Score Card (Top Left)
    if (feedback.atsScore) {
      const atsCard = document.createElement("div");
      atsCard.className = "result-card";
      atsCard.innerHTML = `
        <h3>ATS Resume Score</h3>
        <div class="score-big">${feedback.atsScore.score}%</div>
        <div class="progress-bg">
          <div class="progress-fill" style="width: ${feedback.atsScore.score}%"></div>
        </div>
        <p style="color: #64748b; font-size: 0.9rem;">
          ${feedback.atsScore.score >= 70 ? "Good score! Your resume is ATS-friendly." : "Improvements needed for better compatibility."}
        </p>
      `;
      resultsWrapper.appendChild(atsCard);
    }

    // 3. Identified Skills Card (Top Right)
    const skillsCard = document.createElement("div");
    skillsCard.className = "result-card";
    const skillsList = feedback.skills || ["Analysis", "Professionalism"]; 
    skillsCard.innerHTML = `
      <h3>Identified Skills</h3>
      <div class="skills-list">
        ${skillsList.map(skill => `<span class="skill-badge">${skill}</span>`).join("")}
      </div>
      <p style="color: #64748b; font-size: 0.9rem; margin-top: 15px;">
        Key skills extracted from your content.
      </p>
    `;
    resultsWrapper.appendChild(skillsCard);

    // 4. Overall Impression (Full Width Below Grid)
    const overallAssessment = feedback.feedback?.overallAssessment;
    if (overallAssessment) {
      const overallCard = document.createElement("div");
      overallCard.className = "result-card preview-card";
      overallCard.innerHTML = `
        <h3>Overall Impression</h3>
        <div class="detail-grid">
          <div class="strength-box">
            <h4>Strengths</h4>
            <ul>${overallAssessment.strengths.map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
          <div class="improvement-box">
            <h4>Areas for Improvement</h4>
            <ul>${overallAssessment.areasForImprovement.map(i => `<li>${i}</li>`).join("")}</ul>
          </div>
        </div>
      `;
      resultsDiv.appendChild(overallCard);
    }

    // 5. Detailed Section Loop (Experience, Projects, Education, etc.)
    const sections = feedback.feedback || {};
    for (const [sectionName, sectionData] of Object.entries(sections)) {
      if (sectionName === "overallAssessment") continue; 

      const formattedName = sectionName
        .split(/(?=[A-Z])/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
        .replace("Section", "");

      const sectionCard = document.createElement("div");
      sectionCard.className = "result-card preview-card";
      sectionCard.innerHTML = `
        <h3>${formattedName} Analysis</h3>
        <div class="detail-grid">
          <div class="strength-box">
            <h4 style="color: #10b981;">✓ Strengths</h4>
            <ul>${(sectionData.strengths || []).map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
          <div class="improvement-box">
            <h4 style="color: #f59e0b;">⚠ Improvements</h4>
            <ul>${(sectionData.areasForImprovement || []).map(i => `<li>${i}</li>`).join("")}</ul>
          </div>
        </div>
      `;
      resultsDiv.appendChild(sectionCard);
    }

  } catch (error) {
    loadingDiv.style.display = "none";
    console.error("Error:", error);
    resultsDiv.innerHTML = `
      <div class="error">
        <h2>Error</h2>
        <p>An error occurred while processing your resume. Please try again later.</p>
      </div>`;
  }
});
// Listen for file selection and update the display text
document.getElementById('fileInput').addEventListener('change', function() {
    const fileInput = this;
    const uploadText = document.querySelector('.upload-text');
    
    if (fileInput.files && fileInput.files[0]) {
        // Update the text to the name of the file
        uploadText.textContent = fileInput.files[0].name;
        // Make it blue and bold so it looks selected
        uploadText.style.color = "#3b82f6";
        uploadText.style.fontWeight = "600";
    } else {
        // Reset if no file is chosen
        uploadText.textContent = "Choose PDF file or drag & drop";
        uploadText.style.color = "";
        uploadText.style.fontWeight = "";
    }
});