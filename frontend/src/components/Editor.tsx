import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { 
  MessageSquare, Code, Eye, Play, ArrowUp,
  PanelLeftClose, PanelLeftOpen, Sparkles, FileCode, Folder
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

  const WS_URL = "ws://localhost:8000/api/v1/chat/ws";

  useEffect(() => {
    if (initialPrompt) {
      handleSend(initialPrompt);
    }
  }, [initialPrompt]);

  const handleSend = async (overrideInput?: string) => {
    const textToSend = overrideInput || input;
    if (!textToSend.trim()) return;
    
    setMessages(prev => [...prev, { role: "user", content: textToSend }]);
    if (!overrideInput) setInput("");
    setIsGenerating(true);

    const socket = new WebSocket(WS_URL);
    let accumulatedResponse = "";

    socket.onopen = () => {
      socket.send(textToSend);
    };

    socket.onmessage = (event) => {
      if (event.data === "__END_OF_STREAM__") {
        setIsGenerating(false);
        socket.close();
      } else {
        accumulatedResponse += event.data;
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.role === "assistant") {
            return [...prev.slice(0, -1), { role: "assistant", content: accumulatedResponse }];
          }
          return [...prev, { role: "assistant", content: accumulatedResponse }];
        });
      }
    };

    socket.onerror = (err) => {
      console.error("Socket Error:", err);
      setIsGenerating(false);
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "❌ Connection Error. Please verify backend is running." 
      }]);
    };
  };

  return (
    <div className="h-screen flex flex-col bg-[#000000] text-white font-sans">
      {/* Global Header */}
      <header className="h-14 border-b border-[#2D2D2D] flex items-center justify-between px-4 bg-[#000000]">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-[#D946EF] to-[#8B5CF6]" />
            <span className="font-bold tracking-tight">Showcase AI</span>
          </Link>
          <div className="h-4 w-[1px] bg-[#2D2D2D] mx-2" />
          <span className="text-gray-400 text-sm font-medium">Project Editor</span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="text-gray-300 hover:bg-[#1A1A1A] gap-2">
            <Play className="h-4 w-4 text-[#8B5CF6]" /> Preview
          </Button>
          <Button size="sm" className="bg-[#8B5CF6] hover:bg-[#7C3AED] text-white gap-2">
            <Sparkles className="h-4 w-4" /> Publish
          </Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        {/* Sidebar - Integrated with Dark Aesthetic */}
        <aside className={`${sidebarOpen ? 'w-[350px]' : 'w-0'} border-r border-[#2D2D2D] flex flex-col transition-all duration-300 ease-in-out bg-[#000000] overflow-hidden`}>
          <div className="flex p-2 gap-2 bg-[#000000]">
            <button 
              onClick={() => setActiveTab("chat")} 
              className={`flex-1 py-2 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition-all ${activeTab === "chat" ? "bg-[#1A1A1A] text-white border border-[#333]" : "text-gray-500 hover:text-gray-300"}`}
            >
              <MessageSquare className="h-4 w-4" /> Chat
            </button>
            <button 
              onClick={() => setActiveTab("code")} 
              className={`flex-1 py-2 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition-all ${activeTab === "code" ? "bg-[#1A1A1A] text-white border border-[#333]" : "text-gray-500 hover:text-gray-300"}`}
            >
              <Code className="h-4 w-4" /> Code
            </button>
          </div>

          <div className="flex-1 overflow-hidden flex flex-col">
            {activeTab === "chat" ? (
              <>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${msg.role === "user" ? "bg-[#8B5CF6] text-white" : "bg-[#1A1A1A] border border-[#333] text-gray-200"}`}>
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                  {isGenerating && (
                    <div className="flex justify-start">
                      <div className="bg-[#1A1A1A] border border-[#333] rounded-xl px-4 py-3 flex gap-1.5 animate-pulse">
                        <span className="w-1.5 h-1.5 bg-[#8B5CF6] rounded-full animate-bounce" />
                        <span className="w-1.5 h-1.5 bg-[#8B5CF6] rounded-full animate-bounce [animation-delay:0.2s]" />
                        <span className="w-1.5 h-1.5 bg-[#8B5CF6] rounded-full animate-bounce [animation-delay:0.4s]" />
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4 bg-[#000000] border-t border-[#2D2D2D]">
                  <div className="relative">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSend()}
                      placeholder="Build a professional portfolio..."
                      className="w-full bg-[#1A1A1A] border border-[#333] rounded-xl pl-4 pr-12 py-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#8B5CF6]"
                    />
                    <Button 
                      onClick={() => handleSend()} 
                      disabled={!input.trim() || isGenerating}
                      className="absolute right-1.5 top-1.5 h-8 w-8 bg-[#8B5CF6] hover:bg-[#7C3AED] rounded-lg p-0"
                    >
                      <ArrowUp className="h-4 w-4 text-white" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-400 font-medium"><Folder className="h-4 w-4" /> src</div>
                <div className="pl-6 border-l border-[#2D2D2D] ml-2 space-y-2">
                  <div className="flex items-center gap-2 text-sm text-[#8B5CF6] font-medium bg-[#8B5CF6]/10 p-1.5 rounded-md"><FileCode className="h-4 w-4" /> App.tsx</div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 p-1.5"><FileCode className="h-4 w-4" /> index.css</div>
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Sidebar Toggle Handle */}
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-1/2 -translate-y-1/2 z-20 h-10 w-6 bg-[#1A1A1A] border border-[#333] border-l-0 rounded-r-xl flex items-center justify-center hover:bg-[#2D2D2D] transition-all shadow-xl"
          style={{ left: sidebarOpen ? '350px' : '0px' }}
        >
          {sidebarOpen ? <PanelLeftClose className="h-3.5 w-3.5 text-gray-400" /> : <PanelLeftOpen className="h-3.5 w-3.5 text-gray-400" />}
        </button>

        {/* Main Preview Area - High Contrast White Section */}
        <main className="flex-1 flex flex-col bg-[#0F172A] p-4 relative overflow-hidden">
          <div className="h-10 mb-2 flex items-center justify-between px-2">
            <div className="flex items-center gap-2 text-gray-400 font-medium">
              <Eye className="h-4 w-4" />
              <span className="text-[10px] uppercase tracking-widest">Live Preview</span>
            </div>
            <div className="flex gap-1">
              <div className="h-2 w-2 rounded-full bg-red-500/30" />
              <div className="h-2 w-2 rounded-full bg-yellow-500/30" />
              <div className="h-2 w-2 rounded-full bg-green-500/30" />
            </div>
          </div>
          
          <div className="flex-1 bg-white rounded-xl shadow-2xl overflow-hidden relative border border-white/10">
            {isGenerating && (
              <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex flex-col items-center justify-center z-10">
                <div className="w-12 h-12 border-4 border-[#8B5CF6] border-t-transparent rounded-full animate-spin mb-4" />
                <p className="text-slate-600 font-medium">Architecting your application...</p>
              </div>
            )}
            
            <div className="w-full h-full p-8 flex flex-col items-center justify-center text-center">
              <div className="mb-6">
                 <Sparkles className="h-16 w-16 text-[#8B5CF6]" />
              </div>
              <h2 className="text-3xl font-extrabold text-slate-800 mb-2">Ready to Build</h2>
              <p className="text-slate-500 max-w-md mx-auto text-sm">Enter a prompt in the chat to generate your professional portfolio preview.</p>
              
              <div className="flex gap-4 mt-12">
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[#D946EF] to-[#8B5CF6] opacity-80" />
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[#3B82F6] to-[#8B5CF6] opacity-80" />
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[#F59E0B] to-[#EF4444] opacity-80" />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Editor;