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

// Each dimension has 4 tiers: score < 2, < 3, < 4, <= 5
export const dimensionAdvice = {
  purpose: [
    {
      maxScore: 2,
      headline: "Your team has drifted from its 'why'",
      insight: "When purpose fades, AI fills the vacuum — optimising for speed and output rather than meaning. Your team is likely executing well but questioning less about whether what it's executing actually matters. This is how hollow teams are built: not through neglect, but through efficiency.",
      actions: [
        "Run a 'what would we never do, even if it worked?' session. Make ethics and intent visible again.",
        "Nominate someone to ask 'but why are we doing this?' in every major decision — and mean it.",
        "Review your last 5 major decisions: how many were driven by purpose vs. speed or AI recommendation?",
      ],
    },
    {
      maxScore: 3,
      headline: "Purpose is present — but losing to delivery pressure",
      insight: "Your team knows why it exists, but that conviction doesn't always survive the pressure to ship. AI-generated options get chosen for convenience, and purpose gets cited after the fact rather than driving the decision. The slide from 'at risk' to 'hollow' is quiet and gradual.",
      actions: [
        "Create a weekly ritual: name one decision where purpose overrode efficiency. Celebrate it explicitly.",
        "Before acting on major AI recommendations, make 'does this align with what we stand for?' a required step — not optional.",
        "Revisit your team's stated purpose. Is it still true? Alive? Or is it wallpaper on a slide?",
      ],
    },
    {
      maxScore: 4,
      headline: "Purpose is alive — keep it in the room",
      insight: "Your team operates with genuine conviction most of the time. Purpose shapes decisions more than performance pressure does. The risk now is complacency — purpose fades quietly when everything seems fine and delivery is smooth.",
      actions: [
        "Introduce productive tension: challenge your own purpose regularly. Is it evolving as context changes?",
        "Look for recent moments where efficiency quietly won over purpose — not to blame, but to learn from.",
        "Make purpose explicit in how you evaluate decisions, not just in values statements or onboarding decks.",
      ],
    },
    {
      maxScore: 5,
      headline: "Purpose drives your decisions — protect that",
      insight: "Your team operates from conviction. That is rare. AI amplifies your thinking rather than replacing it because your team knows what it is for. The challenge now is maintaining this as tools evolve, teams grow, and pressure increases.",
      actions: [
        "Document how purpose shapes decision-making — it should be transferable as the team grows or changes.",
        "Schedule a purpose audit twice a year. Even high-performing teams drift when conditions shift.",
        "Share how you do this. Teams like yours make the broader conversation about human-AI collaboration more grounded.",
      ],
    },
  ],
  judgment: [
    {
      maxScore: 2,
      headline: "AI recommendations are moving faster than your scrutiny",
      insight: "Your team is approving outputs it doesn't fully understand. This is the classic hollow team signature: high output, low accountability. People are technically in the loop but not meaningfully so. The output looks fine. The thinking behind it is missing.",
      actions: [
        "Introduce a mandatory challenge: every major AI recommendation requires one person to argue against it before it's adopted.",
        "Ask in your next team meeting: 'Can everyone explain the last three decisions we made in their own words?' Listen carefully.",
        "Create at least one fully human-owned decision each week — no AI input, start to finish.",
      ],
    },
    {
      maxScore: 3,
      headline: "Judgment exists — but speed keeps winning",
      insight: "Critical thinking happens, but not consistently. When time pressure rises, AI outputs get approved faster. The team senses this, but the habit of pushing back hasn't formed yet. The risk is that 'sometimes we question' becomes 'we used to question.'",
      actions: [
        "Designate a 'question keeper' in key meetings — someone whose explicit role is to slow down and interrogate assumptions.",
        "Before finalising any AI-assisted output, ask: 'What did we change? What did we add that AI didn't?' If the answer is nothing — that's your signal.",
        "Celebrate visible disagreement with AI output. Make it a cultural norm, not an awkward exception.",
      ],
    },
    {
      maxScore: 4,
      headline: "Strong judgment — now make it structural",
      insight: "Your team questions AI regularly and can explain its decisions. The habit is forming. Now make it structural so it survives team changes, time pressure, and the next generation of more convincing AI tools.",
      actions: [
        "Build 'why do we believe this?' into your decision records — not just what was decided, but the human reasoning behind it.",
        "Develop team-specific heuristics: what are your red flags for over-relying on AI in your specific domain?",
        "Coach newer team members explicitly in questioning — model it visibly, and name it when you do it.",
      ],
    },
    {
      maxScore: 5,
      headline: "Critical thinking is a team strength — keep sharpening it",
      insight: "Your team doesn't just use AI — it interrogates it. People can articulate their reasoning, challenge outputs, and own their conclusions. This is what it looks like to stay human in an AI-assisted world. The next test: can your judgment keep pace as AI tools become more capable and persuasive?",
      actions: [
        "Stress-test your scrutiny: bring in an AI recommendation your team would be tempted to accept, then work through it rigorously.",
        "Document your approach to AI scrutiny — it's a genuine intellectual asset, not just a habit.",
        "Keep raising the bar: as AI becomes more convincing, your standards for accepting its outputs need to rise with it.",
      ],
    },
  ],
  originality: [
    {
      maxScore: 2,
      headline: "Most of your team's thinking is AI-shaped",
      insight: "Ideas are flowing, but they're being generated, not originated. Meetings feel productive but the thinking is being prompted rather than produced. Over time, the team's ability to think from scratch quietly atrophies — until one day, nobody remembers how.",
      actions: [
        "Track the source of ideas for two weeks: in your last 10 meaningful insights, how many came from a person first? Set a target.",
        "Run AI-free thinking sessions. Give the team a hard problem, no tools — just people. See what emerges.",
        "Introduce pre-meeting thinking: before any AI-assisted session, everyone writes down their own perspective first.",
      ],
    },
    {
      maxScore: 3,
      headline: "Original thinking is happening — but getting crowded out",
      insight: "Original ideas exist in your team, but they're not systematically created or valued. AI-generated options are easier to present and defend, so genuinely new thinking gets crowded out in the time pressure of delivery. The team still has the muscle — it just isn't being used enough.",
      actions: [
        "Ask people to come to key meetings with one idea the AI didn't give them. Make this an explicit expectation.",
        "Actively recognise the person who names something nobody else saw — make originality visible and valued.",
        "Create space between stimulus and response: async thinking time before major decisions, with no AI tools open.",
      ],
    },
    {
      maxScore: 4,
      headline: "Good foundation — now create more space for it",
      insight: "Your team generates real ideas. The conditions are mostly right. The next step is creating more consistent space for genuinely surprising thinking — the kind that AI doesn't produce because it hasn't encountered it yet.",
      actions: [
        "Separate divergence from convergence: keep AI out of the idea generation phase and bring it in only for evaluation.",
        "Celebrate the surprising idea — even when it doesn't get used. Make originality psychologically safe.",
        "Track your most valuable insights from the last quarter. How many were human-originated vs. AI-prompted?",
      ],
    },
    {
      maxScore: 5,
      headline: "Original thought is a team capability — protect it",
      insight: "Your team generates intellectual value that AI cannot replicate, because it comes from genuine human experience, perspective, and curiosity. This is exactly what makes a team irreplaceable — not just productive.",
      actions: [
        "Protect the conditions that make this possible: thinking time, psychological safety, diverse perspectives, and trust.",
        "As AI tools improve, keep asking: where is the human contribution in this? Make the answer visible and explicit.",
        "Your team's originality is worth sharing. Consider making your process more explicit so others can learn from it.",
      ],
    },
  ],
  expertise: [
    {
      maxScore: 2,
      headline: "Deep knowledge may be quietly leaving your team",
      insight: "AI is accelerating delivery while masking a skills gap underneath. Your team produces outputs faster — but could it explain them? Could it catch a sophisticated error? The risk isn't just operational. It's that the team is losing the ability to judge the quality of its own work.",
      actions: [
        "Run an expertise audit: what could your team do independently a year ago that now requires AI assistance? Name it honestly.",
        "Introduce deliberate practice: regular work done without AI tools, specifically to keep skills sharp.",
        "Create knowledge transfer rituals before experienced people leave — not just documentation, but active apprenticeship.",
      ],
    },
    {
      maxScore: 3,
      headline: "Expertise is holding — but not growing",
      insight: "Your team is competent, but AI may be substituting for skill development rather than accelerating it. People are getting faster, not deeper. The craft knowledge that makes genuine judgment possible is plateauing — and plateau often precedes decline.",
      actions: [
        "Redesign how you learn: create conditions where AI deepens expertise through analysis and critique, not just generation.",
        "Ask each team member: 'What do you know now that you didn't a year ago?' If answers are thin, that's your signal.",
        "Identify your most expert people. Are they mentoring? Is their knowledge being transferred or just used?",
      ],
    },
    {
      maxScore: 4,
      headline: "Expertise is growing — keep it transferable",
      insight: "People are genuinely getting sharper. AI is amplifying skill, not replacing it. The risk at this level is that deep knowledge stays with individuals rather than becoming a team asset — and then walks out the door when people leave.",
      actions: [
        "Make expertise visible, transferable, and not dependent on any one person. Build it into how you work, not just who you hire.",
        "Stress-test independence: if your two most expert people were unavailable for a week, what would break?",
        "Always ask: 'Do we understand this better because of AI, or just faster?' Only the first one compounds over time.",
      ],
    },
    {
      maxScore: 5,
      headline: "Your team is genuinely getting smarter — document that",
      insight: "Expertise is deepening across your team. People understand their domain more because of how they use AI, not despite it. That means the quality of your judgment — and your ability to catch errors — is growing alongside your output. That's the goal.",
      actions: [
        "Document how you build expertise. It's a genuine competitive advantage and increasingly rare.",
        "Keep asking: as AI tools improve, does deep domain knowledge still matter? Design your team so the answer is always yes.",
        "Invest in the next generation: apprenticeship, mentorship, and deliberate skill development. When AI levels the output field, expertise is what differentiates.",
      ],
    },
  ],
  balance: [
    {
      maxScore: 2,
      headline: "AI is leading — humans are approving",
      insight: "The balance has tipped. AI is not a tool your team uses — it's the engine your team maintains. The real risk is invisible: when AI is always first and humans react, judgment quietly stops being exercised, even by people who still believe they're in charge.",
      actions: [
        "Redesign decision rights explicitly: which decisions are human-owned, no exceptions? Write it down and enforce it.",
        "Measure human decisions, not just AI outputs. If the ratio is heavily AI-generated, rebalance deliberately.",
        "Run a 'no AI week' on one project. Observe what changes, what's harder, and what's actually better.",
      ],
    },
    {
      maxScore: 3,
      headline: "The balance is off — but recoverable",
      insight: "Humans are still in the room, but AI is driving more of the conversation than it should. The handoff between human and AI judgment is fuzzy — and fuzziness always defaults towards AI over time, because deferring is easier than deciding.",
      actions: [
        "Make the handoff explicit: for each core workflow, define exactly where AI's role ends and human judgment begins.",
        "Ask weekly: 'What did we decide this week that was fully human?' If the answer is vague, that's your signal.",
        "Watch for autonomy creep: AI doing slightly more each month without anyone consciously choosing that.",
      ],
    },
    {
      maxScore: 4,
      headline: "The balance is mostly right — watch for drift",
      insight: "Your team uses AI well. Humans make the calls, AI does the heavy lifting, and people are exercising real judgment. The challenge now is that drift is subtle — the balance shifts gradually without anyone choosing it. Comfort is where hollowing begins.",
      actions: [
        "Audit the balance every quarter: has AI taken on more without an explicit team decision to allow it?",
        "Keep friction alive: make it slightly uncomfortable to accept AI outputs without scrutiny.",
        "As AI tools improve, they'll become more capable and more persuasive. Your human judgment needs to develop alongside them.",
      ],
    },
    {
      maxScore: 5,
      headline: "AI amplifies your team — that's what this looks like",
      insight: "You've found the balance. AI handles what AI should handle. Humans own what humans must own. The line between them is explicit, maintained, and regularly reviewed. This is intentional human-AI collaboration in practice — and it's rarer than most people think.",
      actions: [
        "Document your balance explicitly. It will shift as tools evolve — documentation makes drift visible.",
        "Share how you got here. Most teams haven't. Your experience is genuinely useful to others.",
        "Stay curious: the next generation of AI tools will test this balance again. Keep the question alive.",
      ],
    },
  ],
};

export const scaleLabels = [
  { value: 1, label: "Never" },
  { value: 2, label: "Rarely" },
  { value: 3, label: "Sometimes" },
  { value: 4, label: "Often" },
  { value: 5, label: "Always" },
];
