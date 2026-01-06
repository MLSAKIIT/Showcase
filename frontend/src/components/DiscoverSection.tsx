import { AppCard } from "./AppCard";
import { ArrowRight } from "lucide-react";

const apps = [
  { name: "Iconstack", description: "50,000+ Free SVG Icons", likes: 541, gradient: "bg-gradient-to-br from-violet-600 to-purple-500" },
  { name: "ExamAi", description: "Create, grade, and analyze your exams with AI.", likes: 529, gradient: "bg-gradient-to-br from-blue-600 to-indigo-500" },
  { name: "Attendflow", description: "Event marketing made simple", likes: 528, gradient: "bg-gradient-to-br from-emerald-600 to-green-500" },
  { name: "Creativable", description: "All-in-one CRM, AI Assistant, teams, learning, bookings & presentations", likes: 314, gradient: "bg-gradient-to-br from-amber-600 to-yellow-500" },
  { name: "Opux AI", description: "Every successful app starts here", likes: 269, gradient: "bg-gradient-to-br from-pink-600 to-rose-500" },
  { name: "NeuroTunes AI", description: "Adaptive music streaming engine for on-demand focus and calm", likes: 238, gradient: "bg-gradient-to-br from-cyan-600 to-teal-500" },
  { name: "Pilates Circle", description: "Move, full circle.", likes: 207, gradient: "bg-gradient-to-br from-orange-600 to-red-500" },
  { name: "Createspace", description: "AI Media Made Simple", likes: 137, gradient: "bg-gradient-to-br from-fuchsia-600 to-pink-500" },
];

export const DiscoverSection = () => {
  return (
    <section className="py-24 bg-obsidian-light">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Discover apps</p>
            <h2 className="text-2xl md:text-3xl font-bold">
              Explore what others are building
            </h2>
          </div>
          <a href="#" className="flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors">
            View all <ArrowRight className="h-4 w-4" />
          </a>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {apps.map((app, index) => (
            <AppCard key={index} {...app} />
          ))}
        </div>
      </div>
    </section>
  );
};
