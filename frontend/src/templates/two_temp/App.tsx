import React from 'react';

interface TemplateProps {
    portfolioData: any;
}

/**
 * Placeholder component for two_temp template preview.
 * In the future, this should render the actual template with injected data.
 */
const App: React.FC<TemplateProps> = ({ portfolioData }) => {
    if (!portfolioData) {
        return (
            <div className="p-8 text-center text-gray-400">
                <p>No portfolio data available</p>
            </div>
        );
    }

    const { hero, projects, skills, theme, bio_long } = portfolioData;

    return (
        <div
            className="min-h-screen"
            style={{
                background: `linear-gradient(135deg, ${theme?.primary_color || '#1e3a8a'} 0%, ${theme?.background_color || '#0f172a'} 100%)`,
                color: theme?.text_color || '#f8fafc'
            }}
        >
            {/* Hero Section - Full Width */}
            <header className="min-h-[60vh] flex flex-col justify-center items-center text-center p-8">
                <h1 className="text-5xl md:text-6xl font-extrabold mb-4 drop-shadow-lg">
                    {hero?.name || 'Your Name'}
                </h1>
                <p className="text-2xl md:text-3xl font-light opacity-90 mb-6">
                    {hero?.tagline || 'Your Tagline'}
                </p>
                {hero?.bio_short && (
                    <p className="max-w-xl text-lg opacity-80">{hero.bio_short}</p>
                )}
            </header>

            <main className="max-w-5xl mx-auto px-6 pb-16">
                {/* About Section */}
                {bio_long && (
                    <section className="mb-16">
                        <h2 className="text-3xl font-bold mb-6">About Me</h2>
                        <p className="text-lg leading-relaxed opacity-90">{bio_long}</p>
                    </section>
                )}

                {/* Skills Section */}
                {skills && skills.length > 0 && (
                    <section className="mb-16">
                        <h2 className="text-3xl font-bold mb-6">Skills</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {skills.map((category: any, i: number) => (
                                <div
                                    key={i}
                                    className="p-6 rounded-xl"
                                    style={{ background: 'rgba(255,255,255,0.1)' }}
                                >
                                    <h3 className="text-xl font-semibold mb-4">{category.category}</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {category.items?.map((skill: string, j: number) => (
                                            <span
                                                key={j}
                                                className="px-3 py-1 rounded-full text-sm font-medium"
                                                style={{
                                                    background: theme?.accent_color || '#60a5fa',
                                                    color: '#0f172a'
                                                }}
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* Projects Section */}
                {projects && projects.length > 0 && (
                    <section>
                        <h2 className="text-3xl font-bold mb-6">Projects</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {projects.map((project: any, i: number) => (
                                <div
                                    key={i}
                                    className="p-6 rounded-xl transition-transform hover:scale-105"
                                    style={{ background: 'rgba(255,255,255,0.08)' }}
                                >
                                    <h3 className="text-xl font-bold mb-2">{project.title}</h3>
                                    <p className="opacity-80 mb-4">{project.description}</p>
                                    {project.technologies && (
                                        <div className="flex flex-wrap gap-2">
                                            {project.technologies.map((tech: string, j: number) => (
                                                <span
                                                    key={j}
                                                    className="text-xs px-2 py-1 rounded"
                                                    style={{ background: 'rgba(0,0,0,0.3)' }}
                                                >
                                                    {tech}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </main>

            {/* Footer */}
            <footer className="py-8 text-center text-sm opacity-50">
                <p>Template: two_temp | Preview Mode</p>
            </footer>
        </div>
    );
};

export default App;
