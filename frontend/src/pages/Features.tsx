import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { 
  Zap, 
  Palette, 
  Code2, 
  Smartphone, 
  Cloud, 
  Lock, 
  Sparkles, 
  Globe,
  Users,
  Rocket
} from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Development",
    description: "Describe what you want in plain English and watch your ideas come to life instantly.",
  },
  {
    icon: Code2,
    title: "Clean, Production-Ready Code",
    description: "Generated code follows best practices and is ready for deployment without cleanup.",
  },
  {
    icon: Palette,
    title: "Beautiful Design System",
    description: "Access professionally designed components and themes that look stunning out of the box.",
  },
  {
    icon: Smartphone,
    title: "Responsive by Default",
    description: "Every app works flawlessly on desktop, tablet, and mobile devices.",
  },
  {
    icon: Cloud,
    title: "Built-in Backend",
    description: "Database, authentication, and storage included. No external services needed.",
  },
  {
    icon: Lock,
    title: "Enterprise Security",
    description: "SOC2 compliant with row-level security and encrypted data at rest.",
  },
  {
    icon: Globe,
    title: "One-Click Deploy",
    description: "Publish to a custom domain or our fast global CDN with a single click.",
  },
  {
    icon: Users,
    title: "Real-time Collaboration",
    description: "Work together with your team in real-time with built-in version control.",
  },
  {
    icon: Rocket,
    title: "Instant Iterations",
    description: "Make changes and see results immediately. No build times, no waiting.",
  },
];

const Features = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm mb-6">
            <Zap className="h-4 w-4" />
            Powerful Features
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Everything you need
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Build full-stack applications without writing code. From idea to production in minutes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Features;
