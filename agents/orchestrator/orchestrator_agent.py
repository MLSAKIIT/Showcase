<<<<<<< HEAD
# ORCHESTRATOR.PY - Main Agent Orchestration System

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import traceback
from contextlib import asynccontextmanager

# Type aliases for clarity
PipelineStep = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
=======
"""
ORCHESTRATOR.PY
===============

Central coordinator for the Showcase AI agent pipeline.

Pipeline:
1. Data preprocessing
2. Schema building
3. Content generation
4. Validation & enhancement

This module owns:
- Execution order
- Error boundaries
- Agent composition
- Regeneration logic
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from agents.middleware.data_preprocessor import DataPreprocessor
from agents.core.schema_builder import SchemaBuilder
from agents.generation.content_generator import ContentGenerator
from agents.validation.validator import PortfolioValidator
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5

# Logging

logger = logging.getLogger("agents.orchestrator")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Exceptions

class OrchestratorError(Exception):
    """Base orchestrator error."""


class PipelineStageError(OrchestratorError):
    """Raised when a pipeline stage fails."""


class ValidationError(OrchestratorError):
    """Raised when validation fails."""


# Orchestrator

class PipelineStage(str, Enum):
    """Enumeration of pipeline stages for tracking and monitoring."""
    PREPROCESSING = "preprocessing"
    SCHEMA_BUILDING = "schema_building"
    CONTENT_GENERATION = "content_generation"
    VALIDATION = "validation"
    ENHANCEMENT = "enhancement"
    FINALIZATION = "finalization"


class ProcessingStatus(str, Enum):
    """Status of portfolio processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class PipelineMetrics:
    """Metrics collected during pipeline execution."""
    total_duration: float = 0.0
    stage_durations: Dict[str, float] = field(default_factory=dict)
    retry_counts: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    data_quality_score: float = 0.0
    output_quality_score: float = 0.0


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Timeout settings
    preprocessing_timeout: float = 30.0
    schema_building_timeout: float = 60.0
    content_generation_timeout: float = 120.0
    validation_timeout: float = 45.0
    total_pipeline_timeout: float = 300.0
    
    # Quality thresholds
    min_data_quality: float = 0.3
    min_output_quality: float = 0.5
    
    # Feature flags
    enable_caching: bool = True
    enable_metrics: bool = True
    enable_partial_success: bool = True
    strict_validation: bool = False
    
    # Agent configurations
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    schema_config: Dict[str, Any] = field(default_factory=dict)
    generation_config: Dict[str, Any] = field(default_factory=dict)
    validation_config: Dict[str, Any] = field(default_factory=dict)


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    
    def __init__(self, message: str, stage: Optional[PipelineStage] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.stage = stage
        self.original_error = original_error
        self.timestamp = datetime.utcnow()


class ValidationError(PipelineError):
    """Raised when validation fails."""
    pass


class TimeoutError(PipelineError):
    """Raised when a stage times out."""
    pass


class PortfolioOrchestrator:
    """
<<<<<<< HEAD
    Production-ready orchestrator for portfolio generation pipeline.
    
    Features:
    - Comprehensive error handling with retries
    - Timeout management for each stage
    - Metrics collection and monitoring
    - Partial success handling
    - Pipeline state management
    - Graceful degradation
    - Detailed logging and tracing
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the orchestrator with all required agents.
        
        Args:
            config: Configuration for orchestrator behavior
        """
        self.config = config or OrchestratorConfig()
        
        # Import agents (lazy import to avoid circular dependencies)
        from agents.middleware.data_preprocessor import DataPreprocessor
        from agents.core.schema_builder import SchemaBuilder
        from agents.generation.content_generator import ContentGenerator
        from agents.validation.validator import PortfolioValidator
        
        # Initialize all specialized agents with their configs
        try:
            self.preprocessor = DataPreprocessor(self.config.preprocessing_config)
            self.schema_builder = SchemaBuilder(self.config.schema_config)
            self.content_generator = ContentGenerator(self.config.generation_config)
            self.validator = PortfolioValidator(self.config.validation_config)
        except Exception as e:
            logger.error("Failed to initialize agents: %s", str(e), exc_info=True)
            raise PipelineError(f"Agent initialization failed: {str(e)}") from e
        
        # Pipeline state
        self._current_stage: Optional[PipelineStage] = None
        self._processing_start_time: Optional[datetime] = None
        self._metrics: Optional[PipelineMetrics] = None
        
        # Cache for intermediate results (if enabled)
        self._cache: Dict[str, Any] = {}
        
        logger.info("PortfolioOrchestrator initialized successfully")
    
    async def process_resume(
        self, 
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main pipeline execution method with comprehensive error handling.
        
        This method orchestrates the entire transformation with:
        - Timeout management
        - Retry logic
        - Metrics collection
        - Partial success handling
        
        Args:
            parsed_data: Dictionary containing parsed resume data
            user_preferences: Optional user preferences for generation
        
        Returns:
            Complete portfolio configuration ready for frontend
            
        Raises:
            PipelineError: If pipeline fails and cannot recover
            ValidationError: If validation fails in strict mode
            TimeoutError: If pipeline exceeds timeout
        """
        self._processing_start_time = datetime.utcnow()
        self._metrics = PipelineMetrics()
        
        try:
            logger.info(
                "Starting portfolio generation for: %s", 
                parsed_data.get('name', 'Unknown')
            )
            
            # Validate input
            self._validate_input(parsed_data)
            
            # Execute pipeline with timeout
            async with self._pipeline_timeout(self.config.total_pipeline_timeout):
                portfolio = await self._execute_pipeline(parsed_data, user_preferences)
            
            # Add final metadata
            portfolio['metadata'] = self._build_metadata(portfolio)
            
            # Log success metrics
            self._log_completion_metrics()
            
            logger.info("Portfolio generation completed successfully")
            return portfolio
            
        except asyncio.TimeoutError:
            error_msg = f"Pipeline exceeded timeout of {self.config.total_pipeline_timeout}s"
            logger.error(error_msg)
            self._metrics.errors.append(error_msg)
            raise TimeoutError(error_msg, stage=self._current_stage) from None
            
        except ValidationError:
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error in pipeline: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._metrics.errors.append(error_msg)
            
            # Attempt partial recovery if enabled
            if self.config.enable_partial_success:
                return await self._handle_partial_failure(parsed_data, e)
            
            raise PipelineError(error_msg, stage=self._current_stage) from e
    
    async def _execute_pipeline(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute the main pipeline stages."""
        
        # STAGE 1: Preprocessing
        preprocessed_data = await self._execute_stage(
            stage=PipelineStage.PREPROCESSING,
            func=self.preprocessor.preprocess,
            data=parsed_data,
            timeout=self.config.preprocessing_timeout
        )
        
        # Check data quality
        data_quality = preprocessed_data.get('metadata', {}).get('data_quality_score', 0.0)
        self._metrics.data_quality_score = data_quality
        
        if data_quality < self.config.min_data_quality:
            warning = f"Low data quality score: {data_quality:.2f}"
            logger.warning(warning)
            self._metrics.warnings.append(warning)
            
            if self.config.strict_validation:
                raise ValidationError(
                    f"Data quality {data_quality:.2f} below minimum {self.config.min_data_quality}",
                    stage=PipelineStage.PREPROCESSING
                )
        
        # STAGE 2: Schema Building
        schema = await self._execute_stage(
            stage=PipelineStage.SCHEMA_BUILDING,
            func=self.schema_builder.build_schema,
            data=preprocessed_data,
            timeout=self.config.schema_building_timeout
        )
        
        # STAGE 3: Content Generation
        generated_content = await self._execute_stage(
            stage=PipelineStage.CONTENT_GENERATION,
            func=lambda data: self.content_generator.generate(
                schema=schema,
                user_data=data,
                preferences=user_preferences
            ),
            data=preprocessed_data,
            timeout=self.config.content_generation_timeout
        )
        
        # STAGE 4: Validation and Enhancement
        validated_portfolio = await self._execute_stage(
            stage=PipelineStage.VALIDATION,
            func=lambda data: self.validator.validate_and_enhance(
                generated_content,
                original_data=data
            ),
            data=preprocessed_data,
            timeout=self.config.validation_timeout
        )
        
        # Check output quality
        output_quality = validated_portfolio.get('metadata', {}).get('quality_score', 0.0)
        self._metrics.output_quality_score = output_quality
        
        if output_quality < self.config.min_output_quality:
            warning = f"Low output quality score: {output_quality:.2f}"
            logger.warning(warning)
            self._metrics.warnings.append(warning)
        
        return validated_portfolio
    
    async def _execute_stage(
        self,
        stage: PipelineStage,
        func: Callable,
        data: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """
        Execute a single pipeline stage with retry logic and timeout.
        
        Args:
            stage: Pipeline stage identifier
            func: Async function to execute
            data: Input data for the stage
            timeout: Timeout in seconds
            
        Returns:
            Stage output data
            
        Raises:
            TimeoutError: If stage exceeds timeout
            PipelineError: If stage fails after retries
        """
        self._current_stage = stage
        stage_start = datetime.utcnow()
        
        logger.info("Executing stage: %s", stage.value)
        
        for attempt in range(self.config.max_retries):
            try:
                # Execute with timeout
                async with self._pipeline_timeout(timeout):
                    result = await func(data)
                
                # Record success
                duration = (datetime.utcnow() - stage_start).total_seconds()
                self._metrics.stage_durations[stage.value] = duration
                
                logger.info("✓ Stage '%s' completed in %.2fs", stage.value, duration)
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Stage '{stage.value}' timed out after {timeout}s"
                logger.error(error_msg)
                
                if attempt < self.config.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info("Retrying stage '%s' after %.2fs...", stage.value, delay)
                    await asyncio.sleep(delay)
                    continue
                else:
                    self._metrics.errors.append(error_msg)
                    raise TimeoutError(error_msg, stage=stage) from None
                
            except Exception as e:
                error_msg = f"Stage '{stage.value}' failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Track retry
                self._metrics.retry_counts[stage.value] = attempt + 1
                
                if attempt < self.config.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(
                        "Retrying stage '%s' (attempt %d/%d) after %.2fs...",
                        stage.value, attempt + 2, self.config.max_retries, delay
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    self._metrics.errors.append(error_msg)
                    raise PipelineError(error_msg, stage=stage, original_error=e) from e
        
        # Should never reach here
        raise PipelineError(f"Stage '{stage.value}' failed after all retries", stage=stage)
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry with optional exponential backoff."""
        if self.config.exponential_backoff:
            return self.config.retry_delay * (2 ** attempt)
        return self.config.retry_delay
    
    @asynccontextmanager
    async def _pipeline_timeout(self, timeout: float):
        """Context manager for timeout handling."""
        try:
            async with asyncio.timeout(timeout):
                yield
        except asyncio.TimeoutError:
            raise
    
    async def _handle_partial_failure(
        self,
        parsed_data: Dict[str, Any],
        error: Exception
    ) -> Dict[str, Any]:
        """
        Handle partial failure by returning best-effort portfolio.
        
        Args:
            parsed_data: Original input data
            error: The error that caused failure
            
        Returns:
            Partial portfolio with available data
        """
        logger.warning("Attempting partial recovery after error: %s", str(error))
        
        try:
            # Build minimal portfolio from available data
            partial_portfolio = {
                'hero': {
                    'name': parsed_data.get('name', 'Portfolio'),
                    'tagline': 'Professional Portfolio',
                    'email': parsed_data.get('email'),
                },
                'bio': 'Experienced professional with expertise in various technologies.',
                'skills': parsed_data.get('skills', []),
                'projects': self._format_basic_projects(parsed_data.get('projects', [])),
                'experience': parsed_data.get('experience', []),
                'education': parsed_data.get('education', []),
                'links': parsed_data.get('links', {}),
                'status': ProcessingStatus.PARTIAL.value,
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'pipeline': 'showcase-ai',
                    'status': ProcessingStatus.PARTIAL.value,
                    'error': str(error),
                    'failed_stage': self._current_stage.value if self._current_stage else None,
                    'warnings': ['Portfolio generated with partial data due to processing error']
                }
            }
            
            logger.info("Partial portfolio generated successfully")
            return partial_portfolio
            
        except Exception as recovery_error:
            logger.error(
                "Partial recovery failed: %s", 
                str(recovery_error), 
                exc_info=True
            )
            raise PipelineError(
                f"Complete pipeline failure: {str(error)}. Recovery also failed: {str(recovery_error)}"
            ) from error
    
    def _format_basic_projects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        """Format projects into basic structure for partial recovery."""
        formatted = []
        
        for idx, project in enumerate(projects, 1):
            if isinstance(project, dict):
                formatted.append({
                    'title': project.get('title', f'Project {idx}'),
                    'description': project.get('description', ''),
                    'technologies': project.get('technologies', []),
                    'links': project.get('links', {})
                })
            elif isinstance(project, str):
                formatted.append({
                    'title': f'Project {idx}',
                    'description': project,
                    'technologies': [],
                    'links': {}
                })
        
        return formatted
    
    async def regenerate_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section of the portfolio.
        
        Args:
            portfolio: Current portfolio configuration
            section: Section name to regenerate
            preferences: User preferences for regeneration
            
        Returns:
            Updated portfolio with regenerated section
            
        Raises:
            ValueError: If section is invalid
            PipelineError: If regeneration fails
        """
        try:
            logger.info("Regenerating section: %s", section)
            
            # Validate section exists
            if not self._is_valid_section(portfolio, section):
                raise ValueError(f"Invalid section: {section}")
            
            # Extract context
            context = self._extract_section_context(portfolio, section)
            
            # Regenerate with timeout and retry
            new_content = await self._execute_stage(
                stage=PipelineStage.CONTENT_GENERATION,
                func=lambda _: self.content_generator.regenerate_section(
                    section=section,
                    context=context,
                    preferences=preferences
                ),
                data={},
                timeout=60.0
            )
            
            # Update portfolio
            updated_portfolio = self._update_portfolio_section(
                portfolio,
                section,
                new_content
            )
            
            # Validate updated section
            validated = await self._execute_stage(
                stage=PipelineStage.VALIDATION,
                func=lambda _: self.validator.validate_section(
                    updated_portfolio,
                    section
                ),
                data={},
                timeout=30.0
            )
            
            # Update metadata
            if 'metadata' not in validated:
                validated['metadata'] = {}
            validated['metadata']['last_updated'] = datetime.utcnow().isoformat()
            validated['metadata']['updated_sections'] = validated['metadata'].get(
                'updated_sections', []
            ) + [section]
            
            logger.info("✓ Section '%s' regenerated successfully", section)
            return validated
            
        except Exception as e:
            error_msg = f"Failed to regenerate section '{section}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PipelineError(error_msg) from e
    
    def _is_valid_section(self, portfolio: Dict[str, Any], section: str) -> bool:
        """Check if section is valid in the portfolio."""
        # Handle nested sections (e.g., 'projects.0', 'experience.1')
        if '.' in section:
            parts = section.split('.')
            current = portfolio
            
            for part in parts[:-1]:
                if part not in current:
                    return False
                current = current[part]
            
            last_part = parts[-1]
            if last_part.isdigit():
                return isinstance(current, list) and int(last_part) < len(current)
            return last_part in current
        
        # Simple top-level section
        return section in portfolio
    
    def _extract_section_context(
        self,
        portfolio: Dict[str, Any],
        section: str
    ) -> Dict[str, Any]:
        """
        Extract relevant context for section regeneration.
        
        Args:
            portfolio: Current portfolio
            section: Section to regenerate
            
        Returns:
            Context dictionary with relevant information
        """
        # Get current content
        current_content = self._get_section_content(portfolio, section)
        
        # Build comprehensive context
        context = {
            'section': section,
            'current_content': current_content,
            'user_profile': {
                'name': portfolio.get('hero', {}).get('name'),
                'email': portfolio.get('hero', {}).get('email'),
                'skills': portfolio.get('skills', []),
                'title': portfolio.get('hero', {}).get('title'),
            },
            'style_preferences': portfolio.get('metadata', {}).get('style_preferences', {}),
            'existing_tone': self._analyze_tone(portfolio),
            'section_type': self._get_section_type(section)
        }
        
        return context
    
    def _get_section_content(self, portfolio: Dict[str, Any], section: str) -> Any:
        """Get content of a specific section."""
        if '.' in section:
            parts = section.split('.')
            current = portfolio
            
            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current.get(part)
                    
            return current
        
        return portfolio.get(section)
    
    def _get_section_type(self, section: str) -> str:
        """Determine the type of section."""
        if 'hero' in section:
            return 'hero'
        elif 'bio' in section or 'about' in section:
            return 'bio'
        elif 'project' in section:
            return 'project'
        elif 'experience' in section:
            return 'experience'
        elif 'skill' in section:
            return 'skills'
        else:
            return 'other'
    
    def _analyze_tone(self, portfolio: Dict[str, Any]) -> str:
        """Analyze the tone of existing content."""
        # Simple heuristic based on bio content
        bio = portfolio.get('bio', '')
        
        if not bio:
            return 'professional'
        
        # Check for casual indicators
        casual_words = ['love', 'passionate', 'excited', 'enjoy']
        formal_words = ['experience', 'expertise', 'proficient', 'specialized']
        
        bio_lower = bio.lower()
        casual_count = sum(1 for word in casual_words if word in bio_lower)
        formal_count = sum(1 for word in formal_words if word in bio_lower)
        
        if casual_count > formal_count:
            return 'casual'
        elif formal_count > casual_count:
            return 'formal'
        else:
            return 'professional'
    
    def _update_portfolio_section(
=======
    Coordinates all agents to produce a final portfolio.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

        self.preprocessor = DataPreprocessor(
            self.config.get("preprocessing", {})
        )
        self.schema_builder = SchemaBuilder(
            self.config.get("schema", {})
        )
        self.content_generator = ContentGenerator(
            self.config.get("generation", {})
        )
        self.validator = PortfolioValidator(
            self.config.get("validation", {})
        )

        logger.info("PortfolioOrchestrator initialized")

    # -----------------------------------------------------------------
    # Main Pipeline
    # -----------------------------------------------------------------

    async def process_resume(
        self,
        parsed_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full portfolio generation pipeline.
        """

        started_at = datetime.utcnow()

        try:
            logger.info("Pipeline started")

            # 1. Preprocess
            preprocessed = await self.preprocessor.preprocess(parsed_data)

            # 2. Schema
            schema = await self.schema_builder.build_schema(preprocessed)

            # 3. Generation
            generated = await self.content_generator.generate(
                schema=schema,
                user_data=preprocessed,
                preferences=user_preferences,
            )

            # 4. Validation
            validated = await self.validator.validate_and_enhance(
                generated,
                original_data=preprocessed,
            )

            validated["metadata"] = {
                "generated_at": started_at.isoformat() + "Z",
                "pipeline": "showcase-ai",
                "version": "1.0.0",
            }

            logger.info("Pipeline completed successfully")
            return validated

        except ValidationError:
            raise

        except Exception as exc:
            logger.exception("Pipeline failed")
            raise PipelineStageError(str(exc)) from exc

    # -----------------------------------------------------------------
    # Section Regeneration
    # -----------------------------------------------------------------

    async def regenerate_section(
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
        self,
        portfolio: Dict[str, Any],
        section: str,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
<<<<<<< HEAD
        Update a specific section in the portfolio immutably.
        
        Args:
            portfolio: Current portfolio
            section: Section path (supports nested like 'projects.0')
            new_content: New content for the section
            
        Returns:
            Updated portfolio copy
        """
        import copy
        updated = copy.deepcopy(portfolio)
        
        # Handle nested sections
        if '.' in section:
            parts = section.split('.')
            current = updated
            
            # Navigate to parent
            for part in parts[:-1]:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]
            
            # Update final part
            last_part = parts[-1]
            if last_part.isdigit():
                current[int(last_part)] = new_content
            else:
                current[last_part] = new_content
        else:
            updated[section] = new_content
        
        return updated
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """
        Validate input data before processing.
        
        Args:
            data: Input data to validate
            
        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict input, got {type(data)}")
        
        if not data:
            raise ValidationError("Empty input data provided")
        
        # Check for minimum required fields
        has_identifier = data.get('name') or data.get('email')
        has_content = any([
            data.get('skills'),
            data.get('projects'),
            data.get('experience'),
            data.get('education')
        ])
        
        if not has_identifier:
            raise ValidationError("Input must contain 'name' or 'email'")
        
        if not has_content:
            raise ValidationError(
                "Input must contain at least one of: skills, projects, experience, education"
            )
    
    def _build_metadata(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive metadata for the portfolio.
        
        Args:
            portfolio: Generated portfolio
            
        Returns:
            Metadata dictionary
        """
        duration = (datetime.utcnow() - self._processing_start_time).total_seconds()
        self._metrics.total_duration = duration
        
        metadata = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'processing_version': '2.0.0',
            'pipeline': 'showcase-ai',
            'status': ProcessingStatus.COMPLETED.value,
            'performance': {
                'total_duration_seconds': round(duration, 3),
                'stage_durations': {
                    k: round(v, 3) for k, v in self._metrics.stage_durations.items()
                },
                'retry_counts': self._metrics.retry_counts
            },
            'quality': {
                'data_quality_score': round(self._metrics.data_quality_score, 3),
                'output_quality_score': round(self._metrics.output_quality_score, 3)
            },
            'warnings': self._metrics.warnings,
            'errors': self._metrics.errors
        }
        
        # Merge with any existing metadata from portfolio
        if 'metadata' in portfolio:
            existing = portfolio['metadata']
            metadata = {**existing, **metadata}
        
        return metadata
    
    def _log_completion_metrics(self) -> None:
        """Log detailed metrics after pipeline completion."""
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETION METRICS")
        logger.info("=" * 60)
        logger.info("Total Duration: %.3fs", self._metrics.total_duration)
        logger.info("Data Quality: %.3f", self._metrics.data_quality_score)
        logger.info("Output Quality: %.3f", self._metrics.output_quality_score)
        
        if self._metrics.stage_durations:
            logger.info("\nStage Durations:")
            for stage, duration in self._metrics.stage_durations.items():
                logger.info("  %s: %.3fs", stage, duration)
        
        if self._metrics.retry_counts:
            logger.info("\nRetry Counts:")
            for stage, count in self._metrics.retry_counts.items():
                logger.info("  %s: %d retries", stage, count)
        
        if self._metrics.warnings:
            logger.info("\nWarnings (%d):", len(self._metrics.warnings))
            for warning in self._metrics.warnings[:5]:  # Show first 5
                logger.info("  - %s", warning)
        
        if self._metrics.errors:
            logger.info("\nErrors (%d):", len(self._metrics.errors))
            for error in self._metrics.errors:
                logger.info("  - %s", error)
        
        logger.info("=" * 60)
    
    async def export_portfolio(
        self,
        portfolio: Dict[str, Any],
        export_format: str = 'json',
        include_metadata: bool = True
    ) -> str:
        """
        Export portfolio in different formats.
        
        Args:
            portfolio: Complete portfolio configuration
            export_format: Export format ('json', 'yaml', 'html_preview', 'markdown')
            include_metadata: Whether to include metadata in export
            
        Returns:
            Serialized portfolio data
            
        Raises:
            ValueError: If format is unsupported
            PipelineError: If export fails
        """
        try:
            # Prepare data
            export_data = portfolio.copy()
            if not include_metadata and 'metadata' in export_data:
                del export_data['metadata']
            
            if export_format == 'json':
                return json.dumps(export_data, indent=2, ensure_ascii=False)
                
            elif export_format == 'yaml':
                try:
                    import yaml
                    return yaml.dump(
                        export_data,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False
                    )
                except ImportError:
                    raise PipelineError("PyYAML not installed. Install with: pip install pyyaml")
                    
            elif export_format == 'html_preview':
                return self._generate_html_preview(portfolio)
                
            elif export_format == 'markdown':
                return self._generate_markdown(portfolio)
                
            else:
                raise ValueError(
                    f"Unsupported export format: {export_format}. "
                    f"Supported formats: json, yaml, html_preview, markdown"
                )
                
        except Exception as e:
            error_msg = f"Failed to export portfolio as {export_format}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PipelineError(error_msg) from e
    
    def _generate_html_preview(self, portfolio: Dict[str, Any]) -> str:
        """Generate comprehensive HTML preview of portfolio."""
        hero = portfolio.get('hero', {})
        bio = portfolio.get('bio', '')
        skills = portfolio.get('skills', [])
        projects = portfolio.get('projects', [])
        experience = portfolio.get('experience', [])
        education = portfolio.get('education', [])
        links = portfolio.get('links', {})
        
        # Build projects HTML
        projects_html = ''
        for project in projects:
            tech = ', '.join(project.get('technologies', []))
            projects_html += f'''
                <div class="project">
                    <h3>{project.get('title', 'Untitled Project')}</h3>
                    <p>{project.get('description', '')}</p>
                    {f'<p class="tech"><strong>Technologies:</strong> {tech}</p>' if tech else ''}
                </div>
            '''
        
        # Build experience HTML
        experience_html = ''
        for exp in experience:
            experience_html += f'''
                <div class="experience">
                    <h3>{exp.get('position', 'Position')} at {exp.get('company', 'Company')}</h3>
                    <p class="duration">{exp.get('duration', '')}</p>
                    <p>{exp.get('description', '')}</p>
                </div>
            '''
        
        # Build education HTML
        education_html = ''
        for edu in education:
            education_html += f'''
                <div class="education">
                    <h3>{edu.get('institution', 'Institution')}</h3>
                    <p>{edu.get('degree', '')} {f"in {edu.get('field', '')}" if edu.get('field') else ''}</p>
                    {f'<p class="year">{edu.get("year")}</p>' if edu.get('year') else ''}
                </div>
            '''
        
        # Build links HTML
        links_html = ''
        if links:
            links_html = '<div class="links">'
            for name, url in links.items():
                links_html += f'<a href="{url}" target="_blank">{name.title()}</a> '
            links_html += '</div>'
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{hero.get('name', 'Portfolio')} - Preview</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .hero {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: -40px -20px 40px;
        }}
        .hero h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .hero .tagline {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 50px;
        }}
        .section h2 {{
            font-size: 2em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .bio {{
            font-size: 1.1em;
            line-height: 1.8;
            color: #555;
        }}
        .skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .skill {{
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .project, .experience, .education {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #667eea;
            background: #f9f9f9;
        }}
        .project h3, .experience h3, .education h3 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .tech {{
            color: #667eea;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .duration, .year {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .links {{
            margin-top: 30px;
            text-align: center;
        }}
        .links a {{
            display: inline-block;
            margin: 0 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        .links a:hover {{
            background: #764ba2;
        }}
        .footer {{
            text-align: center;
            color: #888;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>{hero.get('name', 'Portfolio')}</h1>
            <p class="tagline">{hero.get('tagline', '')}</p>
            {f'<p>{hero.get("email", "")}</p>' if hero.get('email') else ''}
        </div>

        {f'<div class="section bio"><h2>About</h2><p>{bio}</p></div>' if bio else ''}

        {f'''<div class="section">
            <h2>Skills</h2>
            <div class="skills">
                {''.join(f'<span class="skill">{skill}</span>' for skill in skills)}
            </div>
        </div>''' if skills else ''}

        {f'''<div class="section">
            <h2>Projects</h2>
            {projects_html}
        </div>''' if projects else ''}

        {f'''<div class="section">
            <h2>Experience</h2>
            {experience_html}
        </div>''' if experience else ''}

        {f'''<div class="section">
            <h2>Education</h2>
            {education_html}
        </div>''' if education else ''}

        {links_html}

        <div class="footer">
            <p>Generated by Showcase AI • {datetime.utcnow().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def _generate_markdown(self, portfolio: Dict[str, Any]) -> str:
        """Generate markdown representation of portfolio."""
        hero = portfolio.get('hero', {})
        bio = portfolio.get('bio', '')
        skills = portfolio.get('skills', [])
        projects = portfolio.get('projects', [])
        experience = portfolio.get('experience', [])
        education = portfolio.get('education', [])
        links = portfolio.get('links', {})
        
        md = f"# {hero.get('name', 'Portfolio')}\n\n"
        
        if hero.get('tagline'):
            md += f"*{hero.get('tagline')}*\n\n"
        
        if hero.get('email'):
            md += f"**Email:** {hero.get('email')}\n\n"
        
        if links:
            md += "**Links:** "
            md += " | ".join([f"[{name.title()}]({url})" for name, url in links.items()])
            md += "\n\n"
        
        md += "---\n\n"
        
        if bio:
            md += f"## About\n\n{bio}\n\n"
        
        if skills:
            md += "## Skills\n\n"
            md += ", ".join([f"`{skill}`" for skill in skills])
            md += "\n\n"
        
        if projects:
            md += "## Projects\n\n"
            for project in projects:
                md += f"### {project.get('title', 'Untitled Project')}\n\n"
                md += f"{project.get('description', '')}\n\n"
                
                if project.get('technologies'):
                    md += f"**Technologies:** {', '.join(project['technologies'])}\n\n"
                
                if project.get('links'):
                    md += "**Links:** "
                    md += " | ".join([f"[{k}]({v})" for k, v in project['links'].items()])
                    md += "\n\n"
        
        if experience:
            md += "## Experience\n\n"
            for exp in experience:
                md += f"### {exp.get('position', 'Position')} at {exp.get('company', 'Company')}\n\n"
                
                if exp.get('duration'):
                    md += f"*{exp['duration']}*\n\n"
                
                if exp.get('description'):
                    md += f"{exp['description']}\n\n"
        
        if education:
            md += "## Education\n\n"
            for edu in education:
                md += f"### {edu.get('institution', 'Institution')}\n\n"
                
                degree_info = edu.get('degree', '')
                if edu.get('field'):
                    degree_info += f" in {edu['field']}"
                if degree_info:
                    md += f"{degree_info}\n\n"
                
                if edu.get('year'):
                    md += f"*{edu['year']}*\n\n"
        
        md += f"\n---\n\n*Generated by Showcase AI on {datetime.utcnow().strftime('%Y-%m-%d')}*\n"
        
        return md
    
    def get_metrics(self) -> Optional[PipelineMetrics]:
        """Get metrics from the last pipeline execution."""
        return self._metrics
    
    def get_current_stage(self) -> Optional[PipelineStage]:
        """Get the current pipeline stage."""
        return self._current_stage
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all agents.
        
        Returns:
            Health status of all components
        """
        health = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {}
        }
        
        # Check each agent
        agents = {
            'preprocessor': self.preprocessor,
            'schema_builder': self.schema_builder,
            'content_generator': self.content_generator,
            'validator': self.validator
        }
        
        for name, agent in agents.items():
            try:
                # Check if agent has health_check method
                if hasattr(agent, 'health_check'):
                    agent_health = await agent.health_check()
                else:
                    agent_health = {'status': 'ok', 'message': 'Agent initialized'}
                
                health['components'][name] = agent_health
                
            except Exception as e:
                health['components'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health['status'] = 'degraded'
        
        return health
    
    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def __repr__(self) -> str:
        """String representation of orchestrator."""
        return (
            f"PortfolioOrchestrator("
            f"config={self.config}, "
            f"current_stage={self._current_stage}, "
            f"cached_items={len(self._cache)}"
            f")"
        )


# Singleton pattern for global orchestrator instance
_orchestrator_instance: Optional[PortfolioOrchestrator] = None
_orchestrator_lock = asyncio.Lock()


async def get_orchestrator(
    config: Optional[OrchestratorConfig] = None,
    force_new: bool = False
) -> PortfolioOrchestrator:
    """
    Get or create the global orchestrator instance (thread-safe).
    
    Args:
        config: Configuration for orchestrator
        force_new: Force creation of new instance
        
    Returns:
        PortfolioOrchestrator instance
    """
    global _orchestrator_instance
    
    async with _orchestrator_lock:
        if _orchestrator_instance is None or force_new:
            _orchestrator_instance = PortfolioOrchestrator(config)
            logger.info("Created new orchestrator instance")
        
        return _orchestrator_instance


def reset_orchestrator() -> None:
    """Reset the global orchestrator instance."""
    global _orchestrator_instance
    _orchestrator_instance = None
    logger.info("Orchestrator instance reset")


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def test_orchestrator():
        """Test the orchestrator with sample data."""
        
        # Create configuration
        config = OrchestratorConfig(
            max_retries=2,
            total_pipeline_timeout=300.0,
            strict_validation=False,
            enable_partial_success=True
        )
        
        # Initialize orchestrator
        orchestrator = PortfolioOrchestrator(config)
        
        # Sample resume data
        sample_data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1 (555) 123-4567',
            'location': 'San Francisco, CA',
            'summary': 'Experienced software engineer specializing in full-stack development',
            'skills': [
                'Python', 'JavaScript', 'React', 'Node.js', 'AWS',
                'Docker', 'PostgreSQL', 'Redis', 'GraphQL'
            ],
            'projects': [
                {
                    'title': 'E-commerce Platform',
                    'description': 'Built a scalable e-commerce platform serving 100K+ users with React, Node.js, and PostgreSQL',
                    'technologies': ['React', 'Node.js', 'PostgreSQL', 'Redis'],
                    'links': {
                        'github': 'https://github.com/janesmith/ecommerce',
                        'demo': 'https://demo.example.com'
                    }
                },
                {
                    'title': 'AI Chat Application',
                    'description': 'Developed an AI-powered chat application with real-time messaging and sentiment analysis',
                    'technologies': ['Python', 'FastAPI', 'WebSocket', 'TensorFlow'],
                    'links': {
                        'github': 'https://github.com/janesmith/ai-chat'
                    }
                }
            ],
            'experience': [
                {
                    'company': 'Tech Corp',
                    'position': 'Senior Software Engineer',
                    'duration': '2020 - Present',
                    'location': 'San Francisco, CA',
                    'description': 'Led development of microservices architecture, reducing latency by 40%'
                },
                {
                    'company': 'Startup Inc',
                    'position': 'Software Engineer',
                    'duration': '2018 - 2020',
                    'location': 'Remote',
                    'description': 'Built RESTful APIs and integrated third-party services'
                }
            ],
            'education': [
                {
                    'institution': 'University of California',
                    'degree': 'B.S. Computer Science',
                    'field': 'Computer Science',
                    'year': 2018,
                    'gpa': 3.8
                }
            ],
            'links': {
                'github': 'https://github.com/janesmith',
                'linkedin': 'https://linkedin.com/in/janesmith',
                'portfolio': 'https://janesmith.dev'
            }
        }
        
        try:
            print("\n" + "="*60)
            print("TESTING PORTFOLIO ORCHESTRATOR")
            print("="*60 + "\n")
            
            # Test health check
            print("Running health check...")
            health = await orchestrator.health_check()
            print(f"Health Status: {health['status']}\n")
            
            # Process resume
            print("Processing resume...")
            portfolio = await orchestrator.process_resume(sample_data)
            
            print("\n" + "="*60)
            print("PORTFOLIO GENERATED SUCCESSFULLY")
            print("="*60)
            
            # Display results
            print(f"\nHero Name: {portfolio.get('hero', {}).get('name')}")
            print(f"Hero Tagline: {portfolio.get('hero', {}).get('tagline')}")
            print(f"Bio Length: {len(portfolio.get('bio', ''))} characters")
            print(f"Number of Skills: {len(portfolio.get('skills', []))}")
            print(f"Number of Projects: {len(portfolio.get('projects', []))}")
            
            # Display metrics
            metrics = orchestrator.get_metrics()
            if metrics:
                print(f"\nProcessing Time: {metrics.total_duration:.2f}s")
                print(f"Data Quality: {metrics.data_quality_score:.2f}")
                print(f"Output Quality: {metrics.output_quality_score:.2f}")
                
                if metrics.warnings:
                    print(f"\nWarnings: {len(metrics.warnings)}")
                    for warning in metrics.warnings[:3]:
                        print(f"  - {warning}")
            
            # Test export
            print("\n" + "="*60)
            print("TESTING EXPORT FUNCTIONALITY")
            print("="*60 + "\n")
            
            # Export as JSON
            json_export = await orchestrator.export_portfolio(portfolio, 'json')
            print(f"JSON Export: {len(json_export)} characters")
            
            # Export as Markdown
            md_export = await orchestrator.export_portfolio(portfolio, 'markdown')
            print(f"Markdown Export: {len(md_export)} characters")
            
            # Export as HTML
            html_export = await orchestrator.export_portfolio(portfolio, 'html_preview')
            print(f"HTML Export: {len(html_export)} characters")
            
            # Save exports to files
            with open('portfolio_export.json', 'w') as f:
                f.write(json_export)
            with open('portfolio_export.md', 'w') as f:
                f.write(md_export)
            with open('portfolio_export.html', 'w') as f:
                f.write(html_export)
            
            print("\nExports saved to:")
            print("  - portfolio_export.json")
            print("  - portfolio_export.md")
            print("  - portfolio_export.html")
            
            print("\n" + "="*60)
            print("ALL TESTS PASSED!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
    
    # Run test
    asyncio.run(test_orchestrator())
=======
        Regenerate a specific section (hero, bio, project index, etc).
        """

        if not section:
            raise ValidationError("section must be provided")

        logger.info("Regenerating section: %s", section)

        context = self._extract_context(portfolio, section)

        new_content = await self.content_generator.regenerate_section(
            section=section,
            context=context,
            preferences=preferences,
        )

        updated = self._update_section(portfolio, section, new_content)

        validated = await self.validator.validate_section(
            updated,
            section,
        )

        validated.setdefault("metadata", {})
        validated["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        return validated

    # -----------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------

    async def export_portfolio(
        self,
        portfolio: Dict[str, Any],
        format: str = "json",
    ) -> str:
        """
        Export portfolio to supported formats.
        """

        if format == "json":
            return json.dumps(portfolio, indent=2, ensure_ascii=False)

        if format == "yaml":
            try:
                import yaml
            except ImportError as exc:
                raise OrchestratorError("PyYAML not installed") from exc

            return yaml.dump(
                portfolio,
                allow_unicode=True,
                sort_keys=False,
            )

        if format == "html_preview":
            return self._generate_html_preview(portfolio)

        raise ValidationError(f"Unsupported export format: {format}")

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _extract_context(
        self,
        portfolio: Dict[str, Any],
        section: str,
    ) -> Dict[str, Any]:
        return {
            "section": section,
            "current_content": portfolio.get(section),
            "profile": {
                "name": portfolio.get("hero", {}).get("name"),
                "skills": portfolio.get("skills", []),
            },
        }

    def _update_section(
        self,
        portfolio: Dict[str, Any],
        section: str,
        content: Any,
    ) -> Dict[str, Any]:
        updated = dict(portfolio)
        updated[section] = content
        return updated

    def _generate_html_preview(self, portfolio: Dict[str, Any]) -> str:
        hero = portfolio.get("hero", {})
        bio = portfolio.get("bio", "")
        projects = portfolio.get("projects", [])

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{hero.get("name", "Portfolio")}</title>
</head>
<body>
  <h1>{hero.get("name", "")}</h1>
  <p>{hero.get("tagline", "")}</p>

  <h2>About</h2>
  <p>{bio}</p>

  <h2>Projects</h2>
  {"".join(f"<h3>{p.get('title')}</h3><p>{p.get('description')}</p>" for p in projects)}
</body>
</html>
"""


# Singleton Access

_orchestrator: Optional[PortfolioOrchestrator] = None
_lock = asyncio.Lock()


async def get_orchestrator(
    config: Optional[Dict[str, Any]] = None,
    force_new: bool = False,
) -> PortfolioOrchestrator:
    global _orchestrator

    async with _lock:
        if _orchestrator is None or force_new:
            _orchestrator = PortfolioOrchestrator(config)
            logger.info("Created orchestrator instance")

        return _orchestrator
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
