import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { useState } from "react";
import { 
  Book, 
  Rocket, 
  Code2, 
  Database, 
  Lock, 
  Palette,
  ChevronRight,
  Search
} from "lucide-react";

const docSections = [
  {
    title: "Getting Started",
    icon: Rocket,
    items: [
      { title: "Introduction", slug: "introduction" },
      { title: "Quick Start", slug: "quick-start" },
      { title: "Your First App", slug: "first-app" },
    ],
  },
  {
    title: "Core Concepts",
    icon: Book,
    items: [
      { title: "How Showcase Works", slug: "how-it-works" },
      { title: "Project Structure", slug: "project-structure" },
      { title: "Prompting Tips", slug: "prompting-tips" },
    ],
  },
  {
    title: "Frontend",
    icon: Palette,
    items: [
      { title: "Components", slug: "components" },
      { title: "Styling", slug: "styling" },
      { title: "Routing", slug: "routing" },
    ],
  },
  {
    title: "Backend",
    icon: Database,
    items: [
      { title: "Database", slug: "database" },
      { title: "Authentication", slug: "authentication" },
      { title: "API Routes", slug: "api-routes" },
    ],
  },
  {
    title: "Advanced",
    icon: Code2,
    items: [
      { title: "Custom Code", slug: "custom-code" },
      { title: "Integrations", slug: "integrations" },
      { title: "Deployment", slug: "deployment" },
    ],
  },
  {
    title: "Security",
    icon: Lock,
    items: [
      { title: "Best Practices", slug: "security-best-practices" },
      { title: "Row Level Security", slug: "rls" },
      { title: "Environment Variables", slug: "env-vars" },
    ],
  },
];

const Docs = () => {
  const [activeSection, setActiveSection] = useState("introduction");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <div className="container mx-auto px-4 py-24">
        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="hidden lg:block w-64 shrink-0">
            <div className="sticky top-24">
              {/* Search */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search docs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Nav */}
              <nav className="space-y-6">
                {docSections.map((section) => (
                  <div key={section.title}>
                    <div className="flex items-center gap-2 text-sm font-semibold text-foreground mb-2">
                      <section.icon className="h-4 w-4" />
                      {section.title}
                    </div>
                    <ul className="space-y-1 pl-6">
                      {section.items.map((item) => (
                        <li key={item.slug}>
                          <button
                            onClick={() => setActiveSection(item.slug)}
                            className={`w-full text-left text-sm py-1 transition-colors ${
                              activeSection === item.slug
                                ? "text-primary"
                                : "text-muted-foreground hover:text-foreground"
                            }`}
                          >
                            {item.title}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </nav>
            </div>
          </aside>

          {/* Content */}
          <main className="flex-1 min-w-0">
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <span>Docs</span>
                <ChevronRight className="h-4 w-4" />
                <span>Getting Started</span>
                <ChevronRight className="h-4 w-4" />
                <span className="text-foreground">Introduction</span>
              </div>

              <h1 className="text-4xl font-bold mb-6">
                <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
                  Introduction to Showcase
                </span>
              </h1>

              <div className="prose prose-invert max-w-none">
                <p className="text-lg text-muted-foreground mb-6">
                  Showcase is an AI-powered development platform that lets you build web applications 
                  by describing what you want in plain English.
                </p>

                <h2 className="text-2xl font-semibold mt-8 mb-4">What is Showcase?</h2>
                <p className="text-muted-foreground mb-4">
                  Showcase combines the power of large language models with a complete development 
                  environment. Simply describe your app, and Showcase will generate clean, 
                  production-ready code.
                </p>

                <div className="bg-card border border-border rounded-lg p-6 my-6">
                  <h3 className="text-lg font-semibold mb-3">Key Features</h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      Natural language to code generation
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      Built-in database and authentication
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      One-click deployment
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      Real-time collaboration
                    </li>
                  </ul>
                </div>

                <h2 className="text-2xl font-semibold mt-8 mb-4">Getting Started</h2>
                <p className="text-muted-foreground mb-4">
                  Ready to build your first app? Head over to the Quick Start guide to create 
                  your first project in under 5 minutes.
                </p>

                <div className="flex gap-4 mt-6">
                  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                    Quick Start →
                  </button>
                  <button className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-muted transition-colors">
                    View Examples
                  </button>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Docs;
