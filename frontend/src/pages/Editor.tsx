import axios from "axios";
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
  Folder,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import api from "@/lib/api";

// Job status types
type JobStatus = "pending" | "processing" | "ocr_extracting" | "ai_generating" | "validating" | "completed" | "failed" | "cancelled";

interface JobStatusData {
  job_id: string;
  status: JobStatus;
  progress_percentage: number;
  current_stage: string | null;
  error?: {
    message: string;
    details?: any;
  };
  duration_seconds?: number;
  portfolio_id?: string;
}

const Editor = () => {
  const [searchParams] = useSearchParams();
  const initialPrompt = searchParams.get("prompt") || "";
  const attachedFile = searchParams.get("fileName");
  const jobId = searchParams.get("jobId");
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<"chat" | "code">("chat");
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Job status state
  const [jobStatus, setJobStatus] = useState<JobStatusData | null>(null);
  const [portfolioData, setPortfolioData] = useState<any>(null);

  useEffect(() => {
    if (initialPrompt || attachedFile || jobId) {
      const userParts = [];
      if (initialPrompt) userParts.push(initialPrompt);
      if (attachedFile) userParts.push(`[Attached: ${attachedFile}]`);
      if (jobId) userParts.push(`[Job ID: ${jobId}]`);

      const userContent = userParts.join("\n");

      let assistantContent = "";
      if (jobId) {
        assistantContent = `I've received your resume (${attachedFile || "file"}). Job ID: ${jobId}.\n\nI am currently analyzing the document to extract your skills, experience, and projects. Once done, I will generate your portfolio structure.`;
      } else {
        assistantContent = `I'll help you create that! Let me build a ${initialPrompt.includes("landing") ? "landing page" : "web application"} for you.\n\nGenerating your project structure...`;
      }

      setMessages([
        { role: "user", content: userContent },
        { role: "assistant", content: assistantContent }
      ]);

      if (jobId) {
        setIsGenerating(true);
        setJobStatus({
          job_id: jobId,
          status: "pending",
          progress_percentage: 0,
          current_stage: null
        });

        // Poll job status
        const pollJobStatus = async () => {
          try {
            const response = await api.get(`/jobs/${jobId}`);
            const statusData: JobStatusData = response.data;
            setJobStatus(statusData);

            // Update chat message with status
            const statusMessages: Record<JobStatus, string> = {
              pending: "Job queued, waiting to start...",
              processing: "Initializing portfolio generation...",
              ocr_extracting: "Extracting text from your resume...",
              ai_generating: "AI is generating your portfolio content...",
              validating: "Validating and finalizing your portfolio...",
              completed: "Portfolio generation complete!",
              failed: `Generation failed: ${statusData.error?.message || "Unknown error"}`,
              cancelled: "Job was cancelled"
            };

            const statusMessage = statusMessages[statusData.status] || "Processing...";
            
            setMessages(prev => {
              const lastMsg = prev[prev.length - 1];
              if (lastMsg?.role === "assistant" && lastMsg.content.includes("analyzing")) {
                return [...prev.slice(0, -1), {
                  role: "assistant",
                  content: `${statusMessage}\n\nProgress: ${statusData.progress_percentage}%\nStage: ${statusData.current_stage || "Initializing"}`
                }];
              }
              return prev;
            });

            // If completed, fetch portfolio
            if (statusData.status === "completed" && statusData.portfolio_id) {
              try {
                const portfolioResponse = await api.get(`/portfolio/${jobId}`);
                const portfolio = portfolioResponse.data;
                
                // Log portfolio data for debugging
                console.log("✅ Portfolio received:", {
                  id: portfolio.id,
                  full_name: portfolio.full_name,
                  has_content: !!portfolio.content,
                  content_type: typeof portfolio.content,
                  content_keys: portfolio.content ? Object.keys(portfolio.content) : null,
                  hero: portfolio.content?.hero,
                  projects_count: portfolio.content?.projects?.length || 0,
                  skills_count: portfolio.content?.skills?.length || 0
                });
                
                setPortfolioData(portfolio);
                setMessages(prev => [...prev, {
                  role: "assistant",
                  content: "✅ Portfolio generation complete! Your portfolio is ready. Check the preview window."
                }]);
                setIsGenerating(false);
                return true; // Stop polling
              } catch (portfolioError: any) {
                // Handle 202 (still processing) or 404 (not found yet)
                if (portfolioError.response?.status === 202 || portfolioError.response?.status === 404) {
                  // Portfolio not found yet, keep polling
                  return false;
                }
                // For other errors, log and continue polling
                console.error("Error fetching portfolio:", portfolioError);
                console.error("Error details:", portfolioError.response?.data);
                return false;
              }
            }

            // If failed, stop polling
            if (statusData.status === "failed") {
              setIsGenerating(false);
              setMessages(prev => [...prev, {
                role: "assistant",
                content: `❌ Portfolio generation failed.\n\nError: ${statusData.error?.message || "Unknown error"}\n\nPlease try uploading your resume again.`
              }]);
              return true; // Stop polling
            }

            return false; // Continue polling
          } catch (error: any) {
            console.error("Error polling job status:", error);
            if (error.response?.status === 404) {
              // Job not found
              setIsGenerating(false);
              setMessages(prev => [...prev, {
                role: "assistant",
                content: "❌ Job not found. Please check your job ID and try again."
              }]);
              return true; // Stop polling
            }
            return false; // Continue polling on other errors
          }
        };

        // Initial poll
        pollJobStatus();

        // Poll every 2 seconds
        const intervalId = setInterval(async () => {
          const shouldStop = await pollJobStatus();
          if (shouldStop) {
            clearInterval(intervalId);
          }
        }, 2000);

        // Stop polling after 5 minutes
        const timeoutId = setTimeout(() => {
          clearInterval(intervalId);
          if (jobStatus?.status !== "completed" && jobStatus?.status !== "failed") {
            setIsGenerating(false);
            setMessages(prev => [...prev, {
              role: "assistant",
              content: "⏱️ Polling timeout. Please check the job status manually or try again."
            }]);
          }
        }, 300000); // 5 minutes

        return () => {
          clearInterval(intervalId);
          clearTimeout(timeoutId);
        };
      } else {
        setIsGenerating(true);
        setTimeout(() => setIsGenerating(false), 2000);
      }
    }
  }, [initialPrompt, attachedFile, jobId]);

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
                  
                  {/* Job Status Display */}
                  {jobId && jobStatus && (
                    <div className="space-y-3">
                      <Alert className={jobStatus.status === "failed" ? "border-destructive" : jobStatus.status === "completed" ? "border-green-500" : ""}>
                        <div className="flex items-start gap-3">
                          {jobStatus.status === "completed" && <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />}
                          {jobStatus.status === "failed" && <XCircle className="h-5 w-5 text-destructive mt-0.5" />}
                          {(jobStatus.status === "processing" || jobStatus.status === "ocr_extracting" || jobStatus.status === "ai_generating" || jobStatus.status === "validating") && (
                            <Loader2 className="h-5 w-5 text-primary mt-0.5 animate-spin" />
                          )}
                          {jobStatus.status === "pending" && <AlertCircle className="h-5 w-5 text-muted-foreground mt-0.5" />}
                          <div className="flex-1 space-y-2">
                            <AlertTitle className="text-sm font-semibold">
                              {jobStatus.status === "completed" && "Portfolio Ready!"}
                              {jobStatus.status === "failed" && "Generation Failed"}
                              {(jobStatus.status === "processing" || jobStatus.status === "ocr_extracting" || jobStatus.status === "ai_generating" || jobStatus.status === "validating") && "Generating Portfolio..."}
                              {jobStatus.status === "pending" && "Queued"}
                            </AlertTitle>
                            <AlertDescription className="text-xs space-y-2">
                              {jobStatus.status !== "completed" && jobStatus.status !== "failed" && (
                                <>
                                  <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                      <span className="text-muted-foreground">Progress</span>
                                      <span className="font-medium">{jobStatus.progress_percentage}%</span>
                                    </div>
                                    <Progress value={jobStatus.progress_percentage} className="h-2" />
                                  </div>
                                  {jobStatus.current_stage && (
                                    <p className="text-muted-foreground">
                                      Stage: <span className="font-medium capitalize">{jobStatus.current_stage.replace("_", " ")}</span>
                                    </p>
                                  )}
                                </>
                              )}
                              {jobStatus.status === "failed" && jobStatus.error && (
                                <div className="space-y-1">
                                  <p className="text-destructive font-medium">{jobStatus.error.message}</p>
                                  {jobStatus.error.details?.stage && (
                                    <p className="text-xs text-muted-foreground">
                                      Failed at: {jobStatus.error.details.stage}
                                    </p>
                                  )}
                                </div>
                              )}
                              {jobStatus.status === "completed" && (
                                <p className="text-green-600 dark:text-green-400">
                                  Your portfolio has been generated successfully!
                                  {jobStatus.duration_seconds && (
                                    <span className="text-xs text-muted-foreground block mt-1">
                                      Completed in {jobStatus.duration_seconds.toFixed(1)}s
                                    </span>
                                  )}
                                </p>
                              )}
                            </AlertDescription>
                          </div>
                        </div>
                      </Alert>
                    </div>
                  )}
                  
                  {isGenerating && !jobStatus && (
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
              {portfolioData ? (
                <div className="w-full h-full p-8 overflow-auto">
                  <div className="max-w-4xl mx-auto">
                    {/* Debug info - remove in production */}
                    {process.env.NODE_ENV === 'development' && (
                      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-xs">
                        <strong>Debug:</strong> Portfolio ID: {portfolioData.id}, 
                        Content type: {typeof portfolioData.content}, 
                        Keys: {portfolioData.content ? Object.keys(portfolioData.content).join(', ') : 'none'}
                      </div>
                    )}
                    
                    {/* Hero Section */}
                    <div className="mb-8 text-center border-b pb-6">
                      <h1 className="text-4xl font-bold text-gray-800 mb-2">
                        {portfolioData.content?.hero?.name || portfolioData.full_name || "Portfolio"}
                      </h1>
                      {portfolioData.content?.hero?.tagline && (
                        <p className="text-xl text-gray-600 mb-2">{portfolioData.content.hero.tagline}</p>
                      )}
                      {portfolioData.content?.hero?.bio_short && (
                        <p className="text-lg text-gray-700 max-w-2xl mx-auto">{portfolioData.content.hero.bio_short}</p>
                      )}
                      {portfolioData.content?.hero?.email && (
                        <p className="text-sm text-gray-500 mt-2">{portfolioData.content.hero.email}</p>
                      )}
                    </div>

                    {/* About Section */}
                    {(portfolioData.content?.bio_long || portfolioData.content?.bio) && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">About</h2>
                        <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                          {portfolioData.content.bio_long || portfolioData.content.bio}
                        </p>
                      </div>
                    )}

                    {/* Experience Section */}
                    {portfolioData.content?.experience && portfolioData.content.experience.length > 0 && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Experience</h2>
                        <div className="space-y-4">
                          {portfolioData.content.experience.map((exp: any, idx: number) => (
                            <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                              <h3 className="text-lg font-semibold text-gray-800">
                                {exp.role || exp.title} {exp.company && `at ${exp.company}`}
                              </h3>
                              {exp.duration && (
                                <p className="text-sm text-gray-500 mb-2">{exp.duration}</p>
                              )}
                              {exp.description && (
                                <p className="text-gray-700">{exp.description}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Projects Section */}
                    {portfolioData.content?.projects && portfolioData.content.projects.length > 0 && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Projects</h2>
                        <div className="grid gap-4 md:grid-cols-2">
                          {portfolioData.content.projects.map((project: any, idx: number) => (
                            <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                              <h3 className="text-lg font-semibold text-gray-800 mb-2">{project.title || project.name}</h3>
                              {project.description && (
                                <p className="text-gray-700 mb-3 text-sm">{project.description}</p>
                              )}
                              {(project.tech_stack || project.technologies) && (
                                <div className="flex flex-wrap gap-2 mt-2">
                                  {(project.tech_stack || project.technologies || []).map((tech: string, techIdx: number) => (
                                    <span key={techIdx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                      {tech}
                                    </span>
                                  ))}
                                </div>
                              )}
                              {project.url && (
                                <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-sm mt-2 inline-block">
                                  View Project →
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Skills Section */}
                    {portfolioData.content?.skills && portfolioData.content.skills.length > 0 && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Skills</h2>
                        <div className="space-y-4">
                          {portfolioData.content.skills.map((skillCat: any, idx: number) => (
                            <div key={idx} className="border border-gray-200 rounded-lg p-4">
                              <h3 className="font-semibold text-gray-800 mb-3 text-lg">
                                {skillCat.category || skillCat.name || `Category ${idx + 1}`}
                              </h3>
                              <div className="flex flex-wrap gap-2">
                                {(skillCat.items || skillCat.skills || []).map((skill: string, skillIdx: number) => (
                                  <span key={skillIdx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Education Section */}
                    {portfolioData.content?.education && portfolioData.content.education.length > 0 && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Education</h2>
                        <div className="space-y-3">
                          {portfolioData.content.education.map((edu: any, idx: number) => (
                            <div key={idx} className="border-l-4 border-green-500 pl-4 py-2">
                              <h3 className="text-lg font-semibold text-gray-800">
                                {edu.degree || edu.course} {edu.institution && `- ${edu.institution}`}
                              </h3>
                              {edu.year && (
                                <p className="text-sm text-gray-500">{edu.year}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Links Section */}
                    {portfolioData.content?.links && Object.keys(portfolioData.content.links).length > 0 && (
                      <div className="mb-8">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Links</h2>
                        <div className="flex flex-wrap gap-3">
                          {Object.entries(portfolioData.content.links).map(([key, url]: [string, any]) => (
                            <a 
                              key={key} 
                              href={url as string} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                              {key.charAt(0).toUpperCase() + key.slice(1)}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Raw data view for debugging */}
                    {process.env.NODE_ENV === 'development' && (
                      <details className="mt-8 p-4 bg-gray-50 rounded border">
                        <summary className="cursor-pointer font-semibold text-sm text-gray-600">View Raw Portfolio Data</summary>
                        <pre className="mt-2 text-xs overflow-auto max-h-96">
                          {JSON.stringify(portfolioData, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              ) : jobStatus && jobStatus.status !== "completed" ? (
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-gray-600 font-medium mb-2">Generating your portfolio...</p>
                  {jobStatus.current_stage && (
                    <p className="text-sm text-gray-500 capitalize">
                      {jobStatus.current_stage.replace("_", " ")}
                    </p>
                  )}
                  {jobStatus.progress_percentage > 0 && (
                    <div className="mt-4 max-w-xs mx-auto">
                      <Progress value={jobStatus.progress_percentage} className="h-2" />
                      <p className="text-xs text-gray-500 mt-2">{jobStatus.progress_percentage}% complete</p>
                    </div>
                  )}
                </div>
              ) : jobStatus && jobStatus.status === "failed" ? (
                <div className="text-center">
                  <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                  <p className="text-gray-800 font-medium mb-2">Portfolio generation failed</p>
                  {jobStatus.error && (
                    <p className="text-sm text-gray-600 mb-4">{jobStatus.error.message}</p>
                  )}
                  <Button onClick={() => window.location.reload()} variant="outline">
                    Try Again
                  </Button>
                </div>
              ) : (
                <div className="text-center p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Portfolio Preview</h2>
                  <p className="text-gray-600 mb-6">This is where your generated portfolio will appear</p>
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
