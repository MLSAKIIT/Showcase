import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-glow-purple to-glow-pink" />
          <span className="text-xl font-bold">Showcase</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Features
          </Link>
          <Link to="/templates" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Templates
          </Link>
          <Link to="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Pricing
          </Link>
          <Link to="/discover" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Discover
          </Link>
          <Link to="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Docs
          </Link>
        </nav>

        {/* Auth Buttons */}
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
            Log in
          </Button>
          <Button size="sm" className="bg-foreground text-background hover:bg-foreground/90">
            Get started
          </Button>
        </div>
      </div>
    </header>
  );
};
