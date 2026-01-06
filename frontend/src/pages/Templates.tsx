import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { TemplateCard } from "@/components/TemplateCard";

const templates = [
  { title: "SaaS Dashboard", description: "Modern dashboard for SaaS apps", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-blue/30" },
  { title: "E-commerce Store", description: "Full-featured online store", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-purple/30" },
  { title: "Portfolio Site", description: "Showcase your work beautifully", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-pink/30" },
  { title: "Blog Platform", description: "Start your content journey", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-pink/30" },
  { title: "Landing Page", description: "High-converting landing pages", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-purple/30" },
  { title: "Admin Panel", description: "Powerful admin interface", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-blue/30" },
  { title: "Social Network", description: "Connect people together", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-blue/30" },
  { title: "Task Manager", description: "Stay organized and productive", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-pink/30" },
  { title: "Booking System", description: "Schedule appointments easily", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-purple/30" },
];

const Templates = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Templates
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Start with a pre-built template and customize it to your needs. All templates are fully editable.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template, index) => (
            <TemplateCard key={index} {...template} />
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Templates;
