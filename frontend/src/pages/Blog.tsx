import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

const blogPosts = [
  {
    title: "Building Modern Web Apps with AI",
    excerpt: "Learn how AI is transforming the way we build web applications and what it means for developers.",
    date: "Jan 5, 2026",
    category: "AI",
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop",
  },
  {
    title: "The Future of No-Code Development",
    excerpt: "Exploring the trends and technologies shaping the future of no-code and low-code platforms.",
    date: "Jan 2, 2026",
    category: "Trends",
    image: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop",
  },
  {
    title: "Design Systems That Scale",
    excerpt: "How to build and maintain design systems that grow with your team and product.",
    date: "Dec 28, 2025",
    category: "Design",
    image: "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600&h=400&fit=crop",
  },
  {
    title: "Performance Optimization Tips",
    excerpt: "Essential techniques for making your web applications faster and more efficient.",
    date: "Dec 20, 2025",
    category: "Performance",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
  },
];

const Blog = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
              Blog
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Insights, tutorials, and updates from the Showcase team.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {blogPosts.map((post, index) => (
            <article
              key={index}
              className="group bg-card border border-border rounded-xl overflow-hidden hover:border-primary/50 transition-all duration-300 cursor-pointer"
            >
              <div className="aspect-video overflow-hidden">
                <img
                  src={post.image}
                  alt={post.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <div className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                    {post.category}
                  </span>
                  <span className="text-xs text-muted-foreground">{post.date}</span>
                </div>
                <h2 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                  {post.title}
                </h2>
                <p className="text-muted-foreground text-sm">{post.excerpt}</p>
              </div>
            </article>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Blog;
