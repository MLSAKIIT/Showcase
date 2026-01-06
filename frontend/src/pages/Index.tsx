import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { TemplatesSection } from "@/components/TemplatesSection";
import { DiscoverSection } from "@/components/DiscoverSection";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Hero />
      <TemplatesSection />
      <DiscoverSection />
      <Footer />
    </div>
  );
};

export default Index;
