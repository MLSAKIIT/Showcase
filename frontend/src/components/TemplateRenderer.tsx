import React, { Suspense, lazy } from 'react';
import { Loader2 } from 'lucide-react';

interface TemplateRendererProps {
    templateId: string;
    data: any;
}

// Map template IDs to their lazy-loaded components
// In a real WebContainer, this would be a virtual file system. 
// For this MVP, we map known templates to specific paths in src/templates.
const templateMap: Record<string, React.LazyExoticComponent<any>> = {
    // We will need to ensure these paths exist
    "one_temp": lazy(() => import('@/templates/one_temp/App')),
    "two_temp": lazy(() => import('@/templates/two_temp/App')),
    // Fallbacks
    "default": lazy(() => import('@/templates/one_temp/App'))
};

export const TemplateRenderer: React.FC<TemplateRendererProps> = ({ templateId, data }) => {
    const TemplateComponent = templateMap[templateId] || templateMap["default"];

    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-primary mb-2" />
                <p className="text-sm text-gray-500">Loading template {templateId}...</p>
            </div>
        }>
            {/* We inject the data as a prop named 'portfolioData' */}
            <TemplateComponent portfolioData={data} />
        </Suspense>
    );
};
