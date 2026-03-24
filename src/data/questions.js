export const dimensions = [
  {
    id: "purpose",
    title: "Purposeful Decision-Making",
    description:
      "The 'purpose layer' decides what should — and should not — be done. It must remain human.",
    icon: "◎",
    questions: [
      {
        id: "p1",
        text: "When your team faces an important decision, members actively debate what *should* be done — not just what is most efficient or what AI recommends.",
      },
      {
        id: "p2",
        text: "Your team can articulate what it would refuse to do, even if an AI system recommended it.",
      },
      {
        id: "p3",
        text: "Your team regularly revisits and challenges its own purpose — it is a living conviction, not just a slide or a target.",
      },
    ],
  },
  {
    id: "judgment",
    title: "Judgment & Critical Thinking",
    description:
      "Healthy teams question AI recommendations. Hollow teams approve outputs faster than they understand them.",
    icon: "◈",
    questions: [
      {
        id: "j1",
        text: "When AI provides a recommendation, team members regularly challenge or question it before acting.",
      },
      {
        id: "j2",
        text: "Team members can explain the reasoning behind recent major decisions in their own words — not by referencing the AI output.",
      },
      {
        id: "j3",
        text: "Your team deliberately slows down to think deeply, rather than always optimizing for speed of delivery.",
      },
    ],
  },
  {
    id: "originality",
    title: "Original Thinking",
    description:
      "Hollow teams fill meetings with confident voices but fewer original ideas. Where does your team's thinking come from?",
    icon: "◇",
    questions: [
      {
        id: "o1",
        text: "Original ideas regularly emerge from your team that were not prompted by an AI tool.",
      },
      {
        id: "o2",
        text: "In meetings, meaningful time is spent on genuinely new thinking — not just reviewing or validating AI-generated options.",
      },
      {
        id: "o3",
        text: "Your team surfaces perspectives that surprise or challenge you — viewpoints that AI alone would not have produced.",
      },
    ],
  },
  {
    id: "expertise",
    title: "Expertise & Craft",
    description:
      "Teams can look productive on every metric while deep craft knowledge quietly disappears. Is yours growing or eroding?",
    icon: "◆",
    questions: [
      {
        id: "e1",
        text: "The depth of domain expertise in your team is growing — people are getting sharper, not just faster.",
      },
      {
        id: "e2",
        text: "If your AI tools were unavailable for a week, your team could still function effectively and make sound decisions.",
      },
      {
        id: "e3",
        text: "When experienced team members leave, their knowledge and judgment stay in the team — it does not leave with them.",
      },
    ],
  },
  {
    id: "balance",
    title: "Human-AI Balance",
    description:
      "AI can amplify human capability or quietly replace it. Which is happening in your team?",
    icon: "◉",
    questions: [
      {
        id: "b1",
        text: "AI in your team acts as a thinking partner — humans make the final calls and actively exercise judgment.",
      },
      {
        id: "b2",
        text: "Team members are making more meaningful, substantive decisions than they were a year ago — not fewer.",
      },
      {
        id: "b3",
        text: "If your team's output has grown, it is because people are thinking better — not because thinking has been offloaded.",
      },
    ],
  },
];

export const interpretations = [
  {
    min: 4.0,
    max: 5.0,
    label: "Amplifying",
    color: "#22c55e",
    tagline: "AI is making your team sharper.",
    description:
      "Your team is on the right side of this challenge. AI is genuinely amplifying human judgment, not replacing it. People think, challenge, and own their decisions. Keep designing deliberately — this takes constant attention to maintain.",
  },
  {
    min: 3.0,
    max: 3.99,
    label: "At Risk",
    color: "#f59e0b",
    tagline: "Signs of hollowing are visible.",
    description:
      "Your team shows real strengths, but warning signs are emerging. Some thinking is being outsourced quietly. The dashboards probably look fine — which is exactly why this moment is easy to miss. Act now, before the patterns deepen.",
  },
  {
    min: 2.0,
    max: 2.99,
    label: "Hollow",
    color: "#f97316",
    tagline: "Your team's thinking muscles are eroding.",
    description:
      "The hollow team pattern is taking hold. Output may still be flowing, but something essential is missing. People are approving more than they are thinking. Expertise is leaving quietly. This requires deliberate, intentional redesign — not just better tools.",
  },
  {
    min: 1.0,
    max: 1.99,
    label: "Critical",
    color: "#ef4444",
    tagline: "Urgent intervention required.",
    description:
      "The hollow team pattern is deeply embedded. The real risk here is not that AI is replacing people — it is that it has replaced the need for people to think. You are not losing jobs. You are losing judgment. This requires urgent structural redesign of how intelligence flows through your team.",
  },
];

export const scaleLabels = [
  { value: 1, label: "Never" },
  { value: 2, label: "Rarely" },
  { value: 3, label: "Sometimes" },
  { value: 4, label: "Often" },
  { value: 5, label: "Always" },
];
