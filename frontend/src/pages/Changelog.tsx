import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

const changelogEntries = [
  {
    date: "January 2026",
    version: "2.5.0",
    changes: [
      { type: "feature", text: "Added AI-powered code suggestions" },
      { type: "feature", text: "New obsidian dark theme" },
      { type: "improvement", text: "Faster build times" },
    ],
  },
  {
    date: "December 2025",
    version: "2.4.0",
    changes: [
      { type: "feature", text: "Real-time collaboration" },
      { type: "improvement", text: "Enhanced template library" },
      { type: "fix", text: "Fixed deployment issues" },
    ],
  },
  {
    date: "November 2025",
    version: "2.3.0",
    changes: [
      { type: "feature", text: "Custom domain support" },
      { type: "feature", text: "Analytics dashboard" },
      { type: "improvement", text: "Better error messages" },
    ],
  },
  {
    date: "October 2025",
    version: "2.2.0",
    changes: [
      { type: "feature", text: "Component marketplace" },
      { type: "improvement", text: "Improved mobile responsiveness" },
      { type: "fix", text: "Various bug fixes" },
    ],
  },
];

const getTypeColor = (type: string) => {
  switch (type) {
    case "feature":
      return "bg-primary/20 text-primary";
    case "improvement":
      return "bg-secondary/20 text-secondary";
    case "fix":
      return "bg-accent/20 text-accent";
    default:
      return "bg-muted text-muted-foreground";
  }
};

const Changelog = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24 max-w-3xl">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Changelog
            </span>
          </h1>
          <p className="text-muted-foreground text-lg">
            Stay up to date with the latest features and improvements.
          </p>
        </div>

        <div className="space-y-12">
          {changelogEntries.map((entry, index) => (
            <div key={index} className="relative pl-8 border-l border-border">
              <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-primary glow-primary" />
              <div className="mb-2">
                <span className="text-sm text-muted-foreground">{entry.date}</span>
                <span className="ml-3 text-sm font-mono bg-card px-2 py-0.5 rounded">
                  v{entry.version}
                </span>
              </div>
              <ul className="space-y-3">
                {entry.changes.map((change, changeIndex) => (
                  <li key={changeIndex} className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded capitalize ${getTypeColor(change.type)}`}>
                      {change.type}
                    </span>
                    <span className="text-foreground">{change.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Changelog;
