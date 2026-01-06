import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { 
  Building2, 
  Shield, 
  Users, 
  Headphones, 
  Lock, 
  BarChart3,
  Globe,
  Zap,
  Check
} from "lucide-react";

const enterpriseFeatures = [
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "SOC2 Type II compliant, SSO, and advanced access controls.",
  },
  {
    icon: Users,
    title: "Team Management",
    description: "Granular permissions, roles, and team workspaces.",
  },
  {
    icon: Headphones,
    title: "Dedicated Support",
    description: "24/7 priority support with dedicated account manager.",
  },
  {
    icon: Lock,
    title: "Data Privacy",
    description: "Data residency options and custom data retention policies.",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Usage insights, audit logs, and compliance reporting.",
  },
  {
    icon: Globe,
    title: "Global Infrastructure",
    description: "Deploy to any region with 99.99% uptime SLA.",
  },
];

const logos = [
  "Acme Corp", "TechStart", "GlobalFin", "DataFlow", "CloudFirst", "ScaleUp"
];

const Enterprise = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main>
        {/* Hero */}
        <section className="container mx-auto px-4 py-24 text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm mb-6">
            <Building2 className="h-4 w-4" />
            Enterprise
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Built for Scale
            </span>
          </h1>
          <p className="text-muted-foreground text-xl max-w-2xl mx-auto mb-8">
            Deploy Showcase across your organization with enterprise-grade security, 
            compliance, and support.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="bg-primary text-primary-foreground">
              Contact Sales
            </Button>
            <Button size="lg" variant="outline">
              Book a Demo
            </Button>
          </div>
        </section>

        {/* Trusted By */}
        <section className="border-y border-border py-12">
          <div className="container mx-auto px-4">
            <p className="text-center text-muted-foreground mb-8">Trusted by industry leaders</p>
            <div className="flex flex-wrap justify-center gap-12">
              {logos.map((logo) => (
                <div key={logo} className="text-xl font-bold text-muted-foreground/50">
                  {logo}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="container mx-auto px-4 py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Enterprise Features</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Everything you need to deploy Showcase at scale with confidence.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {enterpriseFeatures.map((feature, index) => (
              <div
                key={index}
                className="p-6 rounded-xl bg-card border border-border"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Comparison */}
        <section className="container mx-auto px-4 py-24">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Enterprise vs Pro</h2>
              <p className="text-muted-foreground">See what's included in Enterprise</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-1"></div>
              <div className="text-center p-4 rounded-t-xl bg-card border border-border">
                <h3 className="font-semibold">Pro</h3>
              </div>
              <div className="text-center p-4 rounded-t-xl bg-primary text-primary-foreground">
                <h3 className="font-semibold">Enterprise</h3>
              </div>

              {[
                { feature: "Unlimited projects", pro: true, enterprise: true },
                { feature: "Custom domains", pro: true, enterprise: true },
                { feature: "Team collaboration", pro: true, enterprise: true },
                { feature: "SSO / SAML", pro: false, enterprise: true },
                { feature: "Audit logs", pro: false, enterprise: true },
                { feature: "Dedicated support", pro: false, enterprise: true },
                { feature: "Custom SLA", pro: false, enterprise: true },
                { feature: "Data residency", pro: false, enterprise: true },
              ].map((row, i) => (
                <>
                  <div key={`f-${i}`} className="p-4 border-b border-border text-sm">
                    {row.feature}
                  </div>
                  <div key={`p-${i}`} className="p-4 border-b border-border text-center bg-card">
                    {row.pro ? <Check className="h-5 w-5 text-primary mx-auto" /> : <span className="text-muted-foreground">—</span>}
                  </div>
                  <div key={`e-${i}`} className="p-4 border-b border-primary/20 text-center bg-primary/10">
                    <Check className="h-5 w-5 text-primary mx-auto" />
                  </div>
                </>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="container mx-auto px-4 py-24">
          <div className="text-center py-16 px-8 rounded-2xl bg-gradient-to-br from-primary/20 via-accent/10 to-secondary/20 border border-primary/30">
            <Zap className="h-12 w-12 text-primary mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
            <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
              Talk to our sales team to learn how Showcase can accelerate your organization's 
              development workflow.
            </p>
            <div className="flex gap-4 justify-center">
              <Button size="lg" className="bg-primary text-primary-foreground">
                Contact Sales
              </Button>
              <Button size="lg" variant="outline">
                Schedule Demo
              </Button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Enterprise;
