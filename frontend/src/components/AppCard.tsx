import { Heart } from "lucide-react";

interface AppCardProps {
  name: string;
  description: string;
  likes: number;
  gradient: string;
}

export const AppCard = ({ name, description, likes, gradient }: AppCardProps) => {
  return (
    <div className="group cursor-pointer">
      <div className={`aspect-video rounded-xl overflow-hidden mb-4 ${gradient} relative`}>
        {/* Mock app content */}
        <div className="absolute inset-0 flex items-center justify-center p-6">
          <div className="w-full h-full bg-obsidian-light/70 backdrop-blur-sm rounded-lg p-4 flex flex-col">
            <div className="h-3 w-1/3 bg-foreground/20 rounded mb-2" />
            <div className="h-2 w-2/3 bg-foreground/10 rounded mb-4" />
            <div className="flex-1 bg-foreground/5 rounded" />
          </div>
        </div>
        {/* Hover effect */}
        <div className="absolute inset-0 bg-background/50 opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      
      <div className="flex items-start gap-3">
        {/* App icon */}
        <div className={`w-12 h-12 rounded-xl ${gradient} flex-shrink-0`} />
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
            {name}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        </div>

        <div className="flex items-center gap-1 text-muted-foreground">
          <Heart className="h-4 w-4" />
          <span className="text-sm">{likes}</span>
        </div>
      </div>
    </div>
  );
};
