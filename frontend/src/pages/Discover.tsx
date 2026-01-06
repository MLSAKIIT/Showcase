import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { AppCard } from "@/components/AppCard";
import { useState } from "react";
import { Search, Filter, TrendingUp, Clock, Star } from "lucide-react";

const categories = ["All", "SaaS", "E-commerce", "Portfolio", "Dashboard", "Social", "Productivity"];

const apps = [
  { name: "FinanceFlow", category: "SaaS", description: "Financial dashboard", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-blue/30", likes: 423 },
  { name: "ShopNow", category: "E-commerce", description: "Online store platform", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-purple/30", likes: 287 },
  { name: "DevPortfolio", category: "Portfolio", description: "Developer portfolio", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-pink/30", likes: 512 },
  { name: "MetricsDash", category: "Dashboard", description: "Analytics dashboard", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-pink/30", likes: 198 },
  { name: "ConnectHub", category: "Social", description: "Social networking app", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-purple/30", likes: 345 },
  { name: "TaskMaster", category: "Productivity", description: "Task management", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-blue/30", likes: 267 },
  { name: "InvoiceGen", category: "SaaS", description: "Invoice generator", gradient: "bg-gradient-to-br from-glow-purple/30 to-glow-blue/30", likes: 189 },
  { name: "FoodieApp", category: "E-commerce", description: "Food delivery app", gradient: "bg-gradient-to-br from-glow-pink/30 to-glow-purple/30", likes: 432 },
  { name: "DesignStudio", category: "Portfolio", description: "Design showcase", gradient: "bg-gradient-to-br from-glow-blue/30 to-glow-pink/30", likes: 378 },
];

const Discover = () => {
  const [activeCategory, setActiveCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"trending" | "recent" | "popular">("trending");

  const filteredApps = apps.filter(app => {
    const matchesCategory = activeCategory === "All" || app.category === activeCategory;
    const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Discover Apps
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Explore apps built by the community. Get inspired and start building your own.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search apps..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-card border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setSortBy("trending")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${sortBy === "trending" ? "bg-primary text-primary-foreground" : "bg-card border border-border hover:bg-muted"}`}
            >
              <TrendingUp className="h-4 w-4" />
              Trending
            </button>
            <button
              onClick={() => setSortBy("recent")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${sortBy === "recent" ? "bg-primary text-primary-foreground" : "bg-card border border-border hover:bg-muted"}`}
            >
              <Clock className="h-4 w-4" />
              Recent
            </button>
            <button
              onClick={() => setSortBy("popular")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${sortBy === "popular" ? "bg-primary text-primary-foreground" : "bg-card border border-border hover:bg-muted"}`}
            >
              <Star className="h-4 w-4" />
              Popular
            </button>
          </div>
        </div>

        {/* Categories */}
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-4 py-2 rounded-full text-sm transition-colors ${
                activeCategory === category
                  ? "bg-primary text-primary-foreground"
                  : "bg-card border border-border text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Apps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredApps.map((app, index) => (
            <AppCard key={index} {...app} />
          ))}
        </div>

        {filteredApps.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground">No apps found matching your criteria.</p>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default Discover;
