import React from 'react';

interface TemplateProps {
    portfolioData: any;
}

/**
 * Placeholder component for one_temp template preview.
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

    const { hero, projects, skills, theme } = portfolioData;

    return (
        <div
            className="min-h-screen p-8"
            style={{
                background: theme?.background_color || '#0a0a0a',
                color: theme?.text_color || '#ffffff'
            }}
        >
            {/* Hero Section */}
            <header className="mb-12 text-center">
                <h1
                    className="text-4xl font-bold mb-2"
                    style={{ color: theme?.primary_color || '#3b82f6' }}
                >
                    {hero?.name || 'Your Name'}
                </h1>
                <p className="text-xl opacity-80">{hero?.tagline || 'Your Tagline'}</p>
                <p className="mt-4 max-w-2xl mx-auto">{hero?.bio_short || ''}</p>
            </header>

            {/* Skills Section */}
            {skills && skills.length > 0 && (
                <section className="mb-12">
                    <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Skills</h2>
                    <div className="flex flex-wrap gap-2">
                        {skills.map((category: any, i: number) => (
                            <div key={i} className="mb-4">
                                <h3 className="font-medium mb-2">{category.category}</h3>
                                <div className="flex flex-wrap gap-2">
                                    {category.items?.map((skill: string, j: number) => (
                                        <span
                                            key={j}
                                            className="px-3 py-1 rounded-full text-sm"
                                            style={{
                                                background: theme?.accent_color || '#4f46e5',
                                                opacity: 0.8
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
                    <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Projects</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {projects.map((project: any, i: number) => (
                            <div
                                key={i}
                                className="p-4 rounded-lg border border-gray-700"
                                style={{ background: 'rgba(255,255,255,0.05)' }}
                            >
                                <h3 className="text-lg font-semibold mb-2">{project.title}</h3>
                                <p className="text-sm opacity-70 mb-3">{project.description}</p>
                                {project.technologies && (
                                    <div className="flex flex-wrap gap-1">
                                        {project.technologies.map((tech: string, j: number) => (
                                            <span key={j} className="text-xs px-2 py-0.5 bg-gray-800 rounded">
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

            {/* Footer */}
            <footer className="mt-16 pt-8 border-t border-gray-700 text-center text-sm opacity-50">
                <p>Template: one_temp | Preview Mode</p>
            </footer>
        </div>
    );
};

export default App;
