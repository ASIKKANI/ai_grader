const { useState } = React;

function PlagiarismCheckerUI() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e) => {
    setSelectedFiles([...e.target.files]);
  };

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) {
      alert("Upload at least one JSON file! 😤");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch("http://127.0.0.1:8000/plagiarism/check", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("RESULTS:", data);
      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Server error occurred!");
    }

    setLoading(false);
  };

  const renderMatches = (matches) => {
    if (!Array.isArray(matches) || matches.length === 0) {
      return <p className="none">No similarity issues ✅</p>;
    }

    return (
      <ul>
        {matches.map((m, i) => (
          <li key={i}>
            Q{m.q1} ↔ Q{m.q2} • {m.similarity?.toFixed(2)}%
          </li>
        ))}
      </ul>
    );
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <div className="results-container">
        <h3>📊 Plagiarism Report</h3>

        <section>
          <h4>🧍 Intra-Student Similarities</h4>
          {results.intra_student_results.length === 0 && (
            <p className="none">No internal plagiarism detected ✅</p>
          )}

          {results.intra_student_results.map((r, i) => (
            <div className="card" key={i}>
              <strong>Student: {r.student_id}</strong>
              {renderMatches(r.matches)}
            </div>
          ))}
        </section>

        <section>
          <h4>👥 Cross-Student Similarities</h4>
          {results.cross_student_results.length === 0 && (
            <p className="none">No cross-student issues detected ✅</p>
          )}

          {results.cross_student_results.map((r, i) => (
            <div className="card" key={i}>
              <strong>{r.student1} & {r.student2}</strong>
              {renderMatches(r.matches)}
            </div>
          ))}
        </section>
      </div>
    );
  };

  return (
    <div className="container">
      <h2>🔍 AI Plagiarism Detector</h2>

      <input className="file-input" type="file" multiple onChange={handleFileUpload} />

      <button className="upload-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Checking..." : "Check Plagiarism ✅"}
      </button>

      {renderResults()}
    </div>
  );
}

ReactDOM.render(<PlagiarismCheckerUI />, document.getElementById("root"));
