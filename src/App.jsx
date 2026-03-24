import { useState } from "react";
import Welcome from "./components/Welcome";
import Assessment from "./components/Assessment";
import Results from "./components/Results";
import "./App.css";

export default function App() {
  const [stage, setStage] = useState("welcome"); // welcome | assessment | results
  const [teamName, setTeamName] = useState("Your Team");
  const [answers, setAnswers] = useState({});

  const handleStart = (name) => {
    setTeamName(name);
    setStage("assessment");
  };

  const handleComplete = (finalAnswers) => {
    setAnswers(finalAnswers);
    setStage("results");
  };

  const handleRestart = () => {
    setAnswers({});
    setStage("welcome");
  };

  return (
    <div className="app">
      {stage === "welcome" && <Welcome onStart={handleStart} />}
      {stage === "assessment" && (
        <Assessment teamName={teamName} onComplete={handleComplete} />
      )}
      {stage === "results" && (
        <Results
          teamName={teamName}
          answers={answers}
          onRestart={handleRestart}
        />
      )}
    </div>
  );
}
