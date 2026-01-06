import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Templates from "./pages/Templates";
import Changelog from "./pages/Changelog";
import Pricing from "./pages/Pricing";
import Blog from "./pages/Blog";
import Features from "./pages/Features";
import Docs from "./pages/Docs";
import Community from "./pages/Community";
import Discover from "./pages/Discover";
import Enterprise from "./pages/Enterprise";
import Editor from "./pages/Editor";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/changelog" element={<Changelog />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/features" element={<Features />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/community" element={<Community />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/enterprise" element={<Enterprise />} />
          <Route path="/editor" element={<Editor />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
