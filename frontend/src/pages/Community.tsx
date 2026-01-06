import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { 
  MessageCircle, 
  Github, 
  Twitter, 
  Youtube,
  Users,
  Trophy,
  Heart,
  ExternalLink
} from "lucide-react";
import { Button } from "@/components/ui/button";

const communityLinks = [
  {
    title: "Discord",
    description: "Join 50,000+ builders in our Discord community",
    icon: MessageCircle,
    color: "from-indigo-500 to-purple-500",
    members: "50K+",
    link: "#",
  },
  {
    title: "GitHub",
    description: "Explore open source projects and contribute",
    icon: Github,
    color: "from-gray-600 to-gray-800",
    members: "15K+",
    link: "#",
  },
  {
    title: "Twitter",
    description: "Follow for updates, tips, and showcases",
    icon: Twitter,
    color: "from-blue-400 to-blue-600",
    members: "30K+",
    link: "#",
  },
  {
    title: "YouTube",
    description: "Tutorials, demos, and community highlights",
    icon: Youtube,
    color: "from-red-500 to-red-700",
    members: "10K+",
    link: "#",
  },
];

const showcaseProjects = [
  {
    title: "TaskFlow",
    author: "Sarah Chen",
    description: "Beautiful project management tool",
    image: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop",
    likes: 234,
  },
  {
    title: "FitTrack",
    author: "Mike Johnson",
    description: "Fitness tracking dashboard",
    image: "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=400&h=300&fit=crop",
    likes: 189,
  },
  {
    title: "RecipeBox",
    author: "Emily Davis",
    description: "Recipe sharing platform",
    image: "https://images.unsplash.com/photo-1466637574441-749b8f19452f?w=400&h=300&fit=crop",
    likes: 312,
  },
];

const Community = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24">
        {/* Hero */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm mb-6">
            <Users className="h-4 w-4" />
            Join the Community
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Built by the Community
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Connect with thousands of builders, share your creations, and learn from the best.
          </p>
        </div>

        {/* Community Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {communityLinks.map((link) => (
            <a
              key={link.title}
              href={link.link}
              className="group p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${link.color} flex items-center justify-center mb-4`}>
                <link.icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-1 flex items-center gap-2">
                {link.title}
                <ExternalLink className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </h3>
              <p className="text-muted-foreground text-sm mb-3">{link.description}</p>
              <div className="flex items-center gap-1 text-primary text-sm">
                <Users className="h-4 w-4" />
                {link.members} members
              </div>
            </a>
          ))}
        </div>

        {/* Community Showcase */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Trophy className="h-6 w-6 text-primary" />
                Community Showcase
              </h2>
              <p className="text-muted-foreground">Featured projects from our community</p>
            </div>
            <Button variant="outline">View All</Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {showcaseProjects.map((project) => (
              <div
                key={project.title}
                className="group rounded-xl bg-card border border-border overflow-hidden hover:border-primary/50 transition-all duration-300 cursor-pointer"
              >
                <div className="aspect-video overflow-hidden">
                  <img
                    src={project.image}
                    alt={project.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-semibold group-hover:text-primary transition-colors">
                    {project.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-3">{project.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">by {project.author}</span>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Heart className="h-4 w-4" />
                      <span className="text-sm">{project.likes}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center py-16 px-8 rounded-2xl bg-gradient-to-br from-primary/10 via-accent/10 to-secondary/10 border border-border">
          <h2 className="text-3xl font-bold mb-4">Ready to join?</h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Start building with Showcase today and become part of our growing community of creators.
          </p>
          <Button size="lg" className="bg-primary text-primary-foreground">
            Get Started for Free
          </Button>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Community;
