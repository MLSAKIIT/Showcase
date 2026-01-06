interface TemplateCardProps {
  title: string;
  description: string;
  gradient: string;
}

export const TemplateCard = ({ title, description, gradient }: TemplateCardProps) => {
  return (
    <div className="group cursor-pointer">
      <div className={`aspect-video rounded-xl overflow-hidden mb-3 ${gradient} relative`}>
        {/* Overlay with mock content */}
        <div className="absolute inset-0 bg-obsidian/20 flex items-center justify-center">
          <div className="w-3/4 h-3/4 bg-obsidian-light/80 backdrop-blur-sm rounded-lg p-4">
            <div className="h-2 w-1/2 bg-foreground/20 rounded mb-2" />
            <div className="h-2 w-3/4 bg-foreground/10 rounded mb-4" />
            <div className="grid grid-cols-3 gap-2">
              <div className="aspect-square bg-foreground/10 rounded" />
              <div className="aspect-square bg-foreground/10 rounded" />
              <div className="aspect-square bg-foreground/10 rounded" />
            </div>
          </div>
        </div>
        {/* Hover effect */}
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
};
