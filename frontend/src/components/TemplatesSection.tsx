import { TemplateCard } from "./TemplateCard";
import { ArrowRight } from "lucide-react";

const templates = [
  { title: "Ecommerce store", description: "Premium design for webstore", gradient: "bg-gradient-to-br from-purple-600 to-pink-500" },
  { title: "Architect portfolio", description: "Firm website & showcase", gradient: "bg-gradient-to-br from-blue-600 to-cyan-500" },
  { title: "Personal blog", description: "Muted, intimate design", gradient: "bg-gradient-to-br from-amber-600 to-orange-500" },
  { title: "Fashion blog", description: "Minimal, playful design", gradient: "bg-gradient-to-br from-rose-600 to-red-500" },
  { title: "Visual landing page", description: "Showcase your company", gradient: "bg-gradient-to-br from-emerald-600 to-teal-500" },
  { title: "Lifestyle Blog", description: "Sophisticated blog design", gradient: "bg-gradient-to-br from-violet-600 to-indigo-500" },
  { title: "Event platform", description: "Find, register, create events", gradient: "bg-gradient-to-br from-sky-600 to-blue-500" },
  { title: "Personal portfolio", description: "Personal work showcase", gradient: "bg-gradient-to-br from-fuchsia-600 to-pink-500" },
];

export const TemplatesSection = () => {
  return (
    <section className="py-24 bg-obsidian">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Discover templates</p>
            <h2 className="text-2xl md:text-3xl font-bold">
              Start your next project with a template
            </h2>
          </div>
          <a href="#" className="flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors">
            View all <ArrowRight className="h-4 w-4" />
          </a>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {templates.map((template, index) => (
            <TemplateCard key={index} {...template} />
          ))}
        </div>
      </div>
    </section>
  );
};
