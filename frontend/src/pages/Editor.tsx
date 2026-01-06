import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { 
  MessageSquare, 
  Code, 
  Eye, 
  Settings, 
  Play, 
  ArrowUp,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  FileCode,
  Folder
} from "lucide-react";
import { Button } from "@/components/ui/button";

const Editor = () => {
  const [searchParams] = useSearchParams();
  const initialPrompt = searchParams.get("prompt") || "";
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<"chat" | "code">("chat");
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
      setMessages([
        { role: "user", content: initialPrompt },
        { role: "assistant", content: `I'll help you create that! Let me build a ${initialPrompt.includes("landing") ? "landing page" : "web application"} for you.\n\nGenerating your project structure...` }
      ]);
      setIsGenerating(true);
      setTimeout(() => setIsGenerating(false), 2000);
    }
  }, [initialPrompt]);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: "user", content: input }]);
    setInput("");
    setIsGenerating(true);
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "I've made those changes. You can see the updated preview on the right." 
      }]);
      setIsGenerating(false);
    }, 1500);
  };

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {/* Top Bar */}
      <header className="h-14 border-b border-border flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-glow-purple to-glow-pink" />
            <span className="font-bold">Showcase</span>
          </Link>
          <span className="text-muted-foreground text-sm">/ My Project</span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <Play className="h-4 w-4" />
            Preview
          </Button>
          <Button size="sm" className="bg-primary text-primary-foreground gap-2">
            <Sparkles className="h-4 w-4" />
            Publish
          </Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'w-80' : 'w-0'} border-r border-border flex flex-col transition-all duration-300 overflow-hidden`}>
          {/* Tabs */}
          <div className="flex border-b border-border">
            <button 
              onClick={() => setActiveTab("chat")}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${activeTab === "chat" ? "text-foreground border-b-2 border-primary" : "text-muted-foreground hover:text-foreground"}`}
            >
              <MessageSquare className="h-4 w-4" />
              Chat
            </button>
            <button 
              onClick={() => setActiveTab("code")}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${activeTab === "code" ? "text-foreground border-b-2 border-primary" : "text-muted-foreground hover:text-foreground"}`}
            >
              <Code className="h-4 w-4" />
              Code
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {activeTab === "chat" ? (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[90%] rounded-lg px-4 py-2 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                  {isGenerating && (
                    <div className="flex justify-start">
                      <div className="bg-card border border-border rounded-lg px-4 py-2">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                          <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                          <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input */}
                <div className="p-4 border-t border-border">
                  <div className="flex gap-2">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSend()}
                      placeholder="Ask Showcase..."
                      className="flex-1 bg-card border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <Button onClick={handleSend} size="icon" disabled={!input.trim()}>
                      <ArrowUp className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer py-1">
                  <Folder className="h-4 w-4" />
                  <span>src</span>
                </div>
                <div className="pl-4 space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer py-1">
                    <FileCode className="h-4 w-4" />
                    <span>App.tsx</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-primary cursor-pointer py-1">
                    <FileCode className="h-4 w-4" />
                    <span>index.tsx</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground cursor-pointer py-1">
                    <FileCode className="h-4 w-4" />
                    <span>styles.css</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Toggle sidebar button */}
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-1 bg-card border border-border rounded-r-lg hover:bg-muted transition-colors"
          style={{ left: sidebarOpen ? '318px' : '0px' }}
        >
          {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        </button>

        {/* Preview Panel */}
        <main className="flex-1 flex flex-col">
          {/* Preview toolbar */}
          <div className="h-10 border-b border-border flex items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Preview</span>
            </div>
            <button className="p-1 hover:bg-muted rounded">
              <Settings className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>

          {/* Preview content */}
          <div className="flex-1 bg-obsidian-lighter p-4 overflow-auto">
            <div className="bg-white rounded-lg shadow-2xl w-full h-full min-h-[400px] flex items-center justify-center">
              {isGenerating ? (
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-gray-600">Generating your app...</p>
                </div>
              ) : (
                <div className="text-center p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Your App Preview</h2>
                  <p className="text-gray-600 mb-6">This is where your generated app will appear</p>
                  <div className="inline-flex gap-4">
                    <div className="w-32 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg" />
                    <div className="w-32 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg" />
                    <div className="w-32 h-20 bg-gradient-to-br from-pink-500 to-orange-500 rounded-lg" />
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Editor;
