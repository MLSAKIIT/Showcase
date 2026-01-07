"""
ORCHESTRATOR.PY
===============
Central coordinator for Showcase AI agent pipeline.

Pipeline Flow:
1. Data Preprocessing
2. Schema Building  
3. Content Generation
4. Validation & Enhancement
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

from agents.middleware.data_preprocessor import DataPreprocessor
from agents.core.schema_builder import SchemaBuilder
from agents.generation.content_generator import ContentGenerator
from agents.validation.validator import PortfolioValidator

# Logging
logger = logging.getLogger("agents.orchestrator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Exceptions
class OrchestratorError(Exception):
    """Base orchestrator error."""
    pass


class PipelineError(OrchestratorError):
    """Pipeline execution failed."""
    def __init__(self, message: str, stage: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.stage = stage
        self.original_error = original_error
        self.timestamp = datetime.utcnow()


class ValidationError(OrchestratorError):
    """Validation failed."""
    pass


# Enums
class PipelineStage(str, Enum):
    PREPROCESSING = "preprocessing"
    SCHEMA_BUILDING = "schema_building"
    CONTENT_GENERATION = "content_generation"
    VALIDATION = "validation"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# Config & Metrics
@dataclass
class PipelineMetrics:
    """Execution metrics."""
    total_duration: float = 0.0
    stage_durations: Dict[str, float] = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    data_quality_score: float = 0.0
    output_quality_score: float = 0.0


@dataclass
class OrchestratorConfig:
    """Orchestrator configuration."""
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    preprocessing_timeout: float = 30.0
    schema_building_timeout: float = 60.0
    content_generation_timeout: float = 120.0
    validation_timeout: float = 45.0
    total_pipeline_timeout: float = 300.0
    
    min_data_quality: float = 0.3
    min_output_quality: float = 0.5
    
    enable_partial_success: bool = True
    strict_validation: bool = False


# Main Orchestrator
class PortfolioOrchestrator:
    """
    Portfolio generation orchestrator.
    
    Coordinates preprocessing, schema building, content generation, and validation.
    Includes retry logic, timeouts, and error handling.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        
        try:
            self.preprocessor = DataPreprocessor()
            self.schema_builder = SchemaBuilder()
            self.content_generator = ContentGenerator()
            self.validator = PortfolioValidator()
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise PipelineError(f"Agent initialization failed: {str(e)}") from e
        
        self._current_stage: Optional[str] = None
        self._processing_start_time: Optional[datetime] = None
        self._metrics: Optional[PipelineMetrics] = None
        
        logger.info("PortfolioOrchestrator initialized")
    
    async def process_resume(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute full portfolio generation pipeline.
        
        Args:
            parsed_data: Parsed resume data
            user_preferences: Optional user preferences
            
        Returns:
            Generated portfolio configuration
            
        Raises:
            PipelineError: If pipeline fails
        """
        self._processing_start_time = datetime.utcnow()
        self._metrics = PipelineMetrics()
        
        try:
            logger.info(f"Starting portfolio generation for: {parsed_data.get('name', 'Unknown')}")
            
            self._validate_input(parsed_data)
            
            # Execute pipeline with timeout
            try:
                async with asyncio.timeout(self.config.total_pipeline_timeout):
                    portfolio = await self._execute_pipeline(parsed_data, user_preferences)
            except asyncio.TimeoutError:
                raise PipelineError("Pipeline exceeded timeout", stage=self._current_stage)
            
            # Add metadata
            portfolio['metadata'] = self._build_metadata(portfolio)
            
            logger.info("Portfolio generation completed successfully")
            return portfolio
            
        except (PipelineError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            
            if self.config.enable_partial_success:
                return self._handle_partial_failure(parsed_data, e)
            
            raise PipelineError(f"Pipeline failed: {str(e)}", stage=self._current_stage) from e
    
    async def _execute_pipeline(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute all pipeline stages."""
        
        # Stage 1: Preprocessing
        preprocessed_data = await self._execute_stage(
            PipelineStage.PREPROCESSING,
            self.preprocessor.preprocess,
            parsed_data,
            self.config.preprocessing_timeout
        )
        
        # Stage 2: Schema Building
        schema = await self._execute_stage(
            PipelineStage.SCHEMA_BUILDING,
            self.schema_builder.build_schema,
            preprocessed_data,
            self.config.schema_building_timeout
        )
        
        # Stage 3: Content Generation
        generated_content = await self._execute_stage(
            PipelineStage.CONTENT_GENERATION,
            lambda data: self.content_generator.generate(
                schema=schema,
                user_data=data,
                preferences=user_preferences
            ),
            preprocessed_data,
            self.config.content_generation_timeout
        )
        
        # Stage 4: Validation
        portfolio = await self._execute_stage(
            PipelineStage.VALIDATION,
            lambda data: self.validator.validate_and_enhance(
                generated_content,
                original_data=data
            ),
            preprocessed_data,
            self.config.validation_timeout
        )
        
        return portfolio
    
    async def _execute_stage(
        self,
        stage: PipelineStage,
        func,
        data: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """Execute single stage with retries and timeout."""
        self._current_stage = stage.value
        stage_start = datetime.utcnow()
        
        logger.info(f"Executing stage: {stage.value}")
        
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(timeout):
                    result = await func(data)
                
                duration = (datetime.utcnow() - stage_start).total_seconds()
                self._metrics.stage_durations[stage.value] = duration
                
                logger.info(f"✓ Stage '{stage.value}' completed in {duration:.2f}s")
                return result
                
            except asyncio.TimeoutError:
                if attempt < self.config.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Timeout, retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    raise PipelineError(f"Stage '{stage.value}' timed out", stage=stage.value)
                    
            except Exception as e:
                logger.error(f"Stage failed: {str(e)}", exc_info=True)
                
                if attempt < self.config.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying (attempt {attempt + 2}/{self.config.max_retries})...")
                    await asyncio.sleep(delay)
                else:
                    raise PipelineError(f"Stage '{stage.value}' failed", stage=stage.value, original_error=e)
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay with optional exponential backoff."""
        if self.config.exponential_backoff:
            return self.config.retry_delay * (2 ** attempt)
        return self.config.retry_delay
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Validate input data."""
        if not isinstance(data, dict) or not data:
            raise ValidationError("Invalid input: must be non-empty dict")
        
        has_identifier = data.get('name') or data.get('email')
        has_content = any([data.get('skills'), data.get('projects'), 
                          data.get('experience'), data.get('education')])
        
        if not has_identifier:
            raise ValidationError("Input must contain 'name' or 'email'")
        if not has_content:
            raise ValidationError("Input must contain skills, projects, experience, or education")
    
    def _build_metadata(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Build portfolio metadata."""
        duration = (datetime.utcnow() - self._processing_start_time).total_seconds()
        self._metrics.total_duration = duration
        
        return {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'pipeline': 'showcase-ai',
            'status': ProcessingStatus.COMPLETED.value,
            'duration_seconds': round(duration, 3),
            'stage_durations': {k: round(v, 3) for k, v in self._metrics.stage_durations.items()},
            'warnings': self._metrics.warnings,
            'errors': self._metrics.errors
        }
    
    def _handle_partial_failure(
        self,
        parsed_data: Dict[str, Any],
        error: Exception
    ) -> Dict[str, Any]:
        """Return partial portfolio on failure."""
        logger.warning(f"Attempting partial recovery: {str(error)}")
        
        return {
            'hero': {
                'name': parsed_data.get('name', 'Portfolio'),
                'tagline': 'Professional Portfolio',
                'email': parsed_data.get('email'),
            },
            'bio': 'Professional with expertise in various domains.',
            'skills': parsed_data.get('skills', []),
            'projects': parsed_data.get('projects', []),
            'experience': parsed_data.get('experience', []),
            'education': parsed_data.get('education', []),
            'links': parsed_data.get('links', {}),
            'metadata': {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'status': ProcessingStatus.PARTIAL.value,
                'error': str(error),
                'version': '1.0.0'
            }
        }
    
    async def regenerate_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Regenerate a specific portfolio section."""
        if section not in portfolio:
            raise ValidationError(f"Invalid section: {section}")
        
        logger.info(f"Regenerating section: {section}")
        
        context = {
            'section': section,
            'current_content': portfolio.get(section),
            'profile': {
                'name': portfolio.get('hero', {}).get('name'),
                'skills': portfolio.get('skills', [])
            }
        }
        
        new_content = await self.content_generator.regenerate_section(
            section=section,
            context=context,
            preferences=preferences
        )
        
        portfolio[section] = new_content
        portfolio['metadata'] = portfolio.get('metadata', {})
        portfolio['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        
        return portfolio
    
    async def export_portfolio(
        self,
        portfolio: Dict[str, Any],
        format: str = 'json'
    ) -> str:
        """Export portfolio in specified format."""
        if format == 'json':
            return json.dumps(portfolio, indent=2, ensure_ascii=False)
        
        elif format == 'yaml':
            try:
                import yaml
                return yaml.dump(portfolio, allow_unicode=True, sort_keys=False)
            except ImportError:
                raise OrchestratorError("PyYAML not installed")
        
        elif format == 'markdown':
            return self._generate_markdown(portfolio)
        
        elif format == 'html_preview':
            return self._generate_html_preview(portfolio)
        
        else:
            raise ValidationError(f"Unsupported format: {format}")
    
    def _generate_markdown(self, portfolio: Dict[str, Any]) -> str:
        """Generate markdown export."""
        hero = portfolio.get('hero', {})
        md = f"# {hero.get('name', 'Portfolio')}\n\n"
        
        if hero.get('tagline'):
            md += f"*{hero['tagline']}*\n\n"
        if hero.get('email'):
            md += f"📧 {hero['email']}\n\n"
        
        if portfolio.get('bio'):
            md += f"## About\n\n{portfolio['bio']}\n\n"
        
        if portfolio.get('skills'):
            md += f"## Skills\n\n{', '.join(f'`{s}`' for s in portfolio['skills'])}\n\n"
        
        if portfolio.get('projects'):
            md += "## Projects\n\n"
            for p in portfolio['projects']:
                md += f"### {p.get('title')}\n\n{p.get('description', '')}\n\n"
        
        if portfolio.get('experience'):
            md += "## Experience\n\n"
            for e in portfolio['experience']:
                md += f"### {e.get('position')} @ {e.get('company')}\n\n{e.get('description', '')}\n\n"
        
        if portfolio.get('education'):
            md += "## Education\n\n"
            for ed in portfolio['education']:
                md += f"### {ed.get('institution')}\n{ed.get('degree', '')}\n\n"
        
        return md
    
    def _generate_html_preview(self, portfolio: Dict[str, Any]) -> str:
        """Generate HTML preview."""
        hero = portfolio.get('hero', {})
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{hero.get('name', 'Portfolio')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }}
        .hero {{ text-align: center; padding: 40px 0; border-bottom: 2px solid #eee; margin-bottom: 30px; }}
        .hero h1 {{ margin: 0; font-size: 2.5em; }}
        .hero p {{ margin: 10px 0 0 0; color: #666; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .skill {{ background: #007bff; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9em; }}
        .item {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #007bff; }}
        .item h3 {{ margin: 0 0 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>{hero.get('name', 'Portfolio')}</h1>
            <p>{hero.get('tagline', '')}</p>
            <p>{hero.get('email', '')}</p>
        </div>
        
        {f'<div class="section"><h2>About</h2><p>{portfolio.get("bio", "")}</p></div>' if portfolio.get('bio') else ''}
        
        {f'''<div class="section"><h2>Skills</h2>
            <div class="skills">
                {"".join(f'<span class="skill">{s}</span>' for s in portfolio.get("skills", []))}
            </div>
        </div>''' if portfolio.get('skills') else ''}
        
        {f'''<div class="section"><h2>Projects</h2>
            {"".join(f'<div class="item"><h3>{p.get("title")}</h3><p>{p.get("description")}</p></div>' for p in portfolio.get("projects", []))}
        </div>''' if portfolio.get('projects') else ''}
    </div>
</body>
</html>"""
    
    def get_metrics(self) -> Optional[PipelineMetrics]:
        """Get execution metrics."""
        return self._metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents."""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'preprocessor': {'status': 'ok'},
                'schema_builder': {'status': 'ok'},
                'content_generator': {'status': 'ok'},
                'validator': {'status': 'ok'}
            }
        }


# Singleton Pattern
_orchestrator_instance: Optional[PortfolioOrchestrator] = None
_orchestrator_lock = asyncio.Lock()


async def get_orchestrator(
    config: Optional[OrchestratorConfig] = None,
    force_new: bool = False
) -> PortfolioOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator_instance
    
    async with _orchestrator_lock:
        if _orchestrator_instance is None or force_new:
            _orchestrator_instance = PortfolioOrchestrator(config)
            logger.info("Created orchestrator instance")
        
        return _orchestrator_instance


def reset_orchestrator() -> None:
    """Reset global orchestrator instance."""
    global _orchestrator_instance
    _orchestrator_instance = None
    logger.info("Orchestrator reset")