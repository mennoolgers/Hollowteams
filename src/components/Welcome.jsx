import { useState } from "react";

export default function Welcome({ onStart }) {
  const [teamName, setTeamName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onStart(teamName.trim() || "Your Team");
  };

  return (
    <div className="welcome">
      <div className="welcome-content">
        <div className="logo-mark">◎</div>
        <h1>Hollow Team Score</h1>
        <p className="tagline">
          Is AI making your team sharper — or more hollow?
        </p>
        <p className="intro">
          Based on the framework by{" "}
          <strong>Menno Olgers</strong>, this assessment measures five
          dimensions of organizational health in the AI era. It takes about{" "}
          <strong>5 minutes</strong> and produces a score your team can act on.
        </p>

        <div className="dimensions-preview">
          <div className="dim-pill">◎ Purpose</div>
          <div className="dim-pill">◈ Judgment</div>
          <div className="dim-pill">◇ Originality</div>
          <div className="dim-pill">◆ Expertise</div>
          <div className="dim-pill">◉ Balance</div>
        </div>

        <form onSubmit={handleSubmit} className="start-form">
          <input
            type="text"
            placeholder="Team name (optional)"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            className="team-input"
            maxLength={60}
          />
          <button type="submit" className="btn-primary">
            Start Assessment →
          </button>
        </form>

        <p className="disclaimer">
          Answer honestly. There are no right answers — only useful ones.
        </p>
      </div>
    </div>
  );
}
