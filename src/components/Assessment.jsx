import { useState } from "react";
import { dimensions, scaleLabels } from "../data/questions";

export default function Assessment({ teamName, onComplete }) {
  const totalQuestions = dimensions.reduce(
    (sum, d) => sum + d.questions.length,
    0
  );
  const [answers, setAnswers] = useState({});
  const [currentDim, setCurrentDim] = useState(0);

  const dimension = dimensions[currentDim];
  const answeredInDim = dimension.questions.filter((q) => answers[q.id] != null).length;
  const dimComplete = answeredInDim === dimension.questions.length;

  const totalAnswered = Object.keys(answers).length;
  const progress = Math.round((totalAnswered / totalQuestions) * 100);

  const handleAnswer = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleNext = () => {
    if (currentDim < dimensions.length - 1) {
      setCurrentDim((d) => d + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      onComplete(answers);
    }
  };

  const handleBack = () => {
    if (currentDim > 0) {
      setCurrentDim((d) => d - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <div className="assessment">
      <header className="assessment-header">
        <div className="header-left">
          <span className="logo-small">◎</span>
          <span className="team-label">{teamName}</span>
        </div>
        <div className="progress-wrap">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-label">{progress}%</span>
        </div>
      </header>

      <div className="assessment-body">
        <div className="dim-nav">
          {dimensions.map((d, i) => (
            <button
              key={d.id}
              className={`dim-nav-dot ${i === currentDim ? "active" : ""} ${
                dimensions[i].questions.every((q) => answers[q.id] != null)
                  ? "done"
                  : ""
              }`}
              onClick={() => setCurrentDim(i)}
              title={d.title}
            />
          ))}
        </div>

        <div className="dim-header">
          <span className="dim-icon">{dimension.icon}</span>
          <div>
            <div className="dim-count">
              Dimension {currentDim + 1} of {dimensions.length}
            </div>
            <h2>{dimension.title}</h2>
          </div>
        </div>
        <p className="dim-description">{dimension.description}</p>

        <div className="questions">
          {dimension.questions.map((q, qi) => (
            <div key={q.id} className="question-card">
              <p className="question-text">
                <span className="q-num">{qi + 1}.</span>{" "}
                {q.text.replace(/\*(.*?)\*/g, "$1")}
              </p>
              <div className="scale">
                {scaleLabels.map(({ value, label }) => (
                  <button
                    key={value}
                    className={`scale-btn ${
                      answers[q.id] === value ? "selected" : ""
                    }`}
                    onClick={() => handleAnswer(q.id, value)}
                  >
                    <span className="scale-num">{value}</span>
                    <span className="scale-label">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="nav-buttons">
          <button
            className="btn-secondary"
            onClick={handleBack}
            disabled={currentDim === 0}
          >
            ← Back
          </button>
          <button
            className="btn-primary"
            onClick={handleNext}
            disabled={!dimComplete}
          >
            {currentDim === dimensions.length - 1 ? "See Results →" : "Next →"}
          </button>
        </div>
      </div>
    </div>
  );
}
