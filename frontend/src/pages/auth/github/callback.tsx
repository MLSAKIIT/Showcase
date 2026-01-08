import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

const GitHubCallback = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        const code = searchParams.get("code");
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        if (error) {
            setStatus("error");
            setErrorMessage(errorDescription || error || "GitHub authentication failed");
            return;
        }

        if (!code) {
            setStatus("error");
            setErrorMessage("No authorization code received from GitHub");
            return;
        }

        // Send the code to your backend for token exchange
        const exchangeCode = async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_API_URL || ""}/api/v1/auth/github/callback`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ code }),
                    credentials: "include", // Include cookies for session management
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || "Failed to authenticate with GitHub");
                }

                const data = await response.json();

                // Store the token if your backend returns one
                if (data.access_token) {
                    localStorage.setItem("auth_token", data.access_token);
                }

                setStatus("success");

                // Redirect to dashboard or home after successful auth
                setTimeout(() => {
                    navigate("/", { replace: true });
                }, 1500);
            } catch (err) {
                setStatus("error");
                setErrorMessage(err instanceof Error ? err.message : "Authentication failed");
            }
        };

        exchangeCode();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-gray-700/50 max-w-md w-full mx-4">
                {status === "loading" && (
                    <div className="text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 mb-6">
                            <svg
                                className="animate-spin h-12 w-12 text-white"
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
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Authenticating...</h2>
                        <p className="text-gray-400">Please wait while we complete your GitHub login</p>
                    </div>
                )}

                {status === "success" && (
                    <div className="text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-6">
                            <svg
                                className="w-8 h-8 text-green-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M5 13l4 4L19 7"
                                />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Success!</h2>
                        <p className="text-gray-400">Redirecting you to the app...</p>
                    </div>
                )}

                {status === "error" && (
                    <div className="text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-500/20 rounded-full mb-6">
                            <svg
                                className="w-8 h-8 text-red-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Authentication Failed</h2>
                        <p className="text-gray-400 mb-6">{errorMessage}</p>
                        <button
                            onClick={() => navigate("/", { replace: true })}
                            className="px-6 py-3 bg-white text-gray-900 font-semibold rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            Return to Home
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GitHubCallback;
