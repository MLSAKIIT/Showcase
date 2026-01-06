import { Paperclip, Palette, MessageSquare, ArrowUp, AudioLines } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export const Hero = () => {
  const [prompt, setPrompt] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (prompt.trim()) {
      navigate(`/editor?prompt=${encodeURIComponent(prompt)}`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-16 gradient-obsidian overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-glow-purple/20 rounded-full blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-glow-pink/20 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-glow-blue/20 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: "2s" }} />
      </div>

      <div className="relative z-10 container mx-auto px-4 text-center">
        {/* Main Heading */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6">
          Build something <span className="text-gradient">Showcase</span>
        </h1>
        
        {/* Subheading */}
        <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
          Create apps and websites by chatting with AI
        </p>

        {/* Chat Input Box */}
        <div className="max-w-2xl mx-auto">
          <div className={`border-gradient rounded-2xl p-1 transition-all duration-300 ${isFocused ? 'glow-purple' : ''}`}>
            <div className="bg-obsidian-light rounded-xl p-4">
              {/* Input area */}
              <div className="min-h-[80px] mb-4">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask Showcase to create a landing page for my..."
                  className="w-full bg-transparent text-foreground placeholder:text-muted-foreground resize-none focus:outline-none text-left min-h-[60px]"
                  rows={2}
                />
              </div>

              {/* Action bar */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <span className="text-lg">+</span>
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <Paperclip className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Attach</span>
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <Palette className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Theme</span>
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <MessageSquare className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Chat</span>
                  </button>
                  <button className="p-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <AudioLines className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={handleSubmit}
                    disabled={!prompt.trim()}
                    className="p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ArrowUp className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
