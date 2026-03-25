import { dimensions, interpretations } from "../data/questions";

function calcScores(answers) {
  const dimScores = dimensions.map((dim) => {
    const vals = dim.questions.map((q) => answers[q.id] || 0);
    const avg = vals.reduce((s, v) => s + v, 0) / vals.length;
    return { id: dim.id, title: dim.title, icon: dim.icon, score: avg };
  });
  const overall =
    dimScores.reduce((s, d) => s + d.score, 0) / dimScores.length;
  return { dimScores, overall };
}

function getInterpretation(score) {
  return interpretations.find((i) => score >= i.min && score <= i.max) || interpretations[interpretations.length - 1];
}

function ScoreRing({ score, color, size = 160 }) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const filled = (score / 5) * circumference;
  const gap = circumference - filled;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#1e293b"
        strokeWidth="12"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth="12"
        strokeDasharray={`${filled} ${gap}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dasharray 0.8s ease" }}
      />
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dominantBaseline="central"
        fill={color}
        fontSize={size * 0.22}
        fontWeight="700"
        fontFamily="inherit"
      >
        {score.toFixed(1)}
      </text>
    </svg>
  );
}

function DimBar({ dim, score, color }) {
  const pct = (score / 5) * 100;
  return (
    <div className="dim-bar">
      <div className="dim-bar-header">
        <span className="dim-bar-icon">{dim.icon}</span>
        <span className="dim-bar-title">{dim.title}</span>
        <span className="dim-bar-score" style={{ color }}>
          {score.toFixed(1)}
        </span>
      </div>
      <div className="dim-bar-track">
        <div
          className="dim-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

export default function Results({ teamName, answers, onRestart }) {
  const { dimScores, overall } = calcScores(answers);
  const interp = getInterpretation(overall);

  const barColor = (score) => {
    if (score >= 4) return "#22c55e";
    if (score >= 3) return "#f59e0b";
    if (score >= 2) return "#f97316";
    return "#ef4444";
  };

  const weakest = [...dimScores].sort((a, b) => a.score - b.score)[0];
  const strongest = [...dimScores].sort((a, b) => b.score - a.score)[0];

  return (
    <div className="results">
      <div className="results-content">
        <header className="results-header">
          <span className="logo-small">◎</span>
          <span className="team-label">{teamName}</span>
        </header>

        <div className="overall-section">
          <ScoreRing score={overall} color={interp.color} size={180} />
          <div className="overall-text">
            <div
              className="interp-label"
              style={{ color: interp.color }}
            >
              {interp.label}
            </div>
            <div className="interp-tagline">{interp.tagline}</div>
            <p className="interp-description">{interp.description}</p>
          </div>
        </div>

        <div className="dim-bars-section">
          <h3>Dimension Breakdown</h3>
          {dimScores.map((d) => (
            <DimBar
              key={d.id}
              dim={d}
              score={d.score}
              color={barColor(d.score)}
            />
          ))}
        </div>

        <div className="insights-section">
          <div className="insight-card insight-strength">
            <div className="insight-label">Strongest dimension</div>
            <div className="insight-dim">
              {strongest.icon} {strongest.title}
            </div>
            <div className="insight-score">{strongest.score.toFixed(1)} / 5</div>
          </div>
          <div className="insight-card insight-weak">
            <div className="insight-label">Most at risk</div>
            <div className="insight-dim">
              {weakest.icon} {weakest.title}
            </div>
            <div className="insight-score">{weakest.score.toFixed(1)} / 5</div>
          </div>
        </div>

        <div className="reflection-section">
          <h3>Questions to bring to your team</h3>
          <ul className="reflection-list">
            <li>
              Which decisions in our team <em>must</em> remain fundamentally
              human, even when AI informs them?
            </li>
            <li>
              Are we approving AI outputs faster than we understand them?
            </li>
            <li>
              Where do we want intelligence to live — and what do people need to
              exercise it responsibly?
            </li>
            <li>
              Is AI making us sharper, or are our thinking muscles quietly
              eroding?
            </li>
          </ul>
        </div>

        <div className="scale-legend">
          <span>Scale: </span>
          <span className="legend-item" style={{ color: "#ef4444" }}>1 Critical</span>
          <span className="legend-item" style={{ color: "#f97316" }}>2 Hollow</span>
          <span className="legend-item" style={{ color: "#f59e0b" }}>3 At Risk</span>
          <span className="legend-item" style={{ color: "#22c55e" }}>4–5 Amplifying</span>
        </div>

        <div className="cta-section">
          <p className="cta-heading">Want to go deeper?</p>
          <p className="cta-sub">
            Follow along for more thinking on intentional human-AI collaboration.
          </p>
          <div className="cta-buttons">
            <a
              className="cta-btn cta-btn-linkedin"
              href="https://www.linkedin.com/in/molgers/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              Follow on LinkedIn
            </a>
            <a
              className="cta-btn cta-btn-substack"
              href="https://substack.com/@mennoolgers"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                <path d="M22.539 8.242H1.46V5.406h21.08v2.836zM1.46 10.812V24L12 18.11 22.54 24V10.812H1.46zM22.54 0H1.46v2.836h21.08V0z"/>
              </svg>
              Subscribe on Substack
            </a>
          </div>
        </div>

        <div className="results-footer">
          <p className="attribution">
            Based on the Hollow Team framework by{" "}
            <strong>Menno Olgers</strong>, inspired by the challenge of
            intentional human-AI collaboration.
          </p>
          <button className="btn-secondary" onClick={onRestart}>
            ← Retake Assessment
          </button>
        </div>
      </div>
    </div>
  );
}
