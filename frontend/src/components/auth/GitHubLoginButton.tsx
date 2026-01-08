import { useState } from "react";

interface GitHubLoginButtonProps {
    className?: string;
    size?: "sm" | "md" | "lg";
    variant?: "default" | "outline";
}

const GitHubLoginButton = ({
    className = "",
    size = "md",
    variant = "default",
}: GitHubLoginButtonProps) => {
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = () => {
        setIsLoading(true);

        // GitHub OAuth configuration
        const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
        const redirectUri = `${window.location.origin}/auth/github/callback`;
        const scope = "read:user user:email"; // Adjust scopes as needed

        // Build GitHub OAuth URL
        const githubAuthUrl = new URL("https://github.com/login/oauth/authorize");
        githubAuthUrl.searchParams.set("client_id", clientId);
        githubAuthUrl.searchParams.set("redirect_uri", redirectUri);
        githubAuthUrl.searchParams.set("scope", scope);

        // Optional: Add state parameter for CSRF protection
        const state = crypto.randomUUID();
        sessionStorage.setItem("github_oauth_state", state);
        githubAuthUrl.searchParams.set("state", state);

        // Redirect to GitHub
        window.location.href = githubAuthUrl.toString();
    };

    const sizeClasses = {
        sm: "px-4 py-2 text-sm gap-2",
        md: "px-6 py-3 text-base gap-3",
        lg: "px-8 py-4 text-lg gap-3",
    };

    const variantClasses = {
        default:
            "bg-gray-900 hover:bg-gray-800 text-white border-transparent",
        outline:
            "bg-transparent hover:bg-gray-100 text-gray-900 border-gray-300 dark:text-white dark:border-gray-600 dark:hover:bg-gray-800",
    };

    return (
        <button
            onClick={handleLogin}
            disabled={isLoading}
            className={`
        inline-flex items-center justify-center font-semibold rounded-lg
        border-2 transition-all duration-200 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
        disabled:opacity-60 disabled:cursor-not-allowed
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
        >
            {isLoading ? (
                <svg
                    className="animate-spin h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                >
                    <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                    />
                    <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                </svg>
            ) : (
                <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                >
                    <path
                        fillRule="evenodd"
                        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                        clipRule="evenodd"
                    />
                </svg>
            )}
            <span>{isLoading ? "Connecting..." : "Continue with GitHub"}</span>
        </button>
    );
};

export default GitHubLoginButton;
