import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { auth } from "@/lib/firebase";
import { onAuthStateChanged, signOut, User } from "firebase/auth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { LogOut, User as UserIcon, LayoutDashboard, Github } from "lucide-react";

export const Header = () => {
  const [user, setUser] = useState<User | null>(null);
  const [githubConnected, setGithubConnected] = useState(false);
  const navigate = useNavigate();

  // Check if GitHub is already connected
  useEffect(() => {
    const token = localStorage.getItem("github_token");
    setGithubConnected(!!token);
  }, []);

  // 🛡️ Listen for Auth State changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      // If Firebase says no user, clear our local token just in case
      if (!currentUser) {
        localStorage.removeItem("token");
      }
    });
    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem("token");
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  // Connect GitHub account for deployment
  const handleConnectGitHub = () => {
    const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
    const redirectUri = `${window.location.origin}/auth/github/callback`;
    const scope = "repo user:email";

    const githubAuthUrl = new URL("https://github.com/login/oauth/authorize");
    githubAuthUrl.searchParams.set("client_id", clientId);
    githubAuthUrl.searchParams.set("redirect_uri", redirectUri);
    githubAuthUrl.searchParams.set("scope", scope);

    const state = `connect_${crypto.randomUUID()}`;
    sessionStorage.setItem("github_oauth_state", state);
    githubAuthUrl.searchParams.set("state", state);

    window.location.href = githubAuthUrl.toString();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6 md:gap-10">
          <Link to="/" className="flex items-center space-x-2">
            <span className="inline-block font-bold text-xl">Showcase AI</span>
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link to="/templates" className="text-sm font-medium transition-colors hover:text-primary">Templates</Link>
            <Link to="/pricing" className="text-sm font-medium transition-colors hover:text-primary">Pricing</Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-10 w-10 border border-primary/20">
                    <AvatarImage src={user.photoURL || ""} alt={user.displayName || "User"} />
                    <AvatarFallback className="bg-primary/10">
                      {user.displayName?.charAt(0) || <UserIcon size={20} />}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.displayName}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate("/editor")}>
                  <LayoutDashboard className="mr-2 h-4 w-4" />
                  <span>My Editor</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={handleConnectGitHub}
                  disabled={githubConnected}
                  className={githubConnected ? "text-green-500" : ""}
                >
                  <Github className="mr-2 h-4 w-4" />
                  <span>{githubConnected ? "GitHub Connected" : "Connect GitHub"}</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => navigate("/login")}>Login</Button>
              <Button onClick={() => navigate("/login")}>Get Started</Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
