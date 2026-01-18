"""
CONTENT_GENERATOR.PY - AI Content Generation Agent (Gemini Integration)
========================================================================

PURPOSE:
This is the creative brain of the pipeline. It uses Google's Gemini LLM to generate
compelling portfolio content from the structured schema.

DATA FLOW IN:
- Portfolio schema (from schema_builder)
- User data (original preprocessed data for context)

DATA FLOW OUT:
- Complete portfolio with AI-generated content:
  * Hero tagline
  * Professional bio
  * Enhanced project descriptions
  * Section content

HOW IT WORKS:
- Uses constrained generation (not plain prompts!)
- Sends schema + strict formatting rules to Gemini
- Generates React components, Tailwind styles, config files
- Maintains consistency across all generated content
- Uses temperature control for creativity vs. accuracy balance

NOTE: THIS CODE IS AI GENERATED, YOUR WORK IS TO ANALYSIS THE CODE AND CHECK THE LOGIC AND MAKE CHANGES
     WHERE REQUIRED
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import os
import hashlib
from functools import wraps

# Google Generative AI (new google.genai package)
try:
    import google.genai as genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "google-genai not installed. Install with: pip install google-genai"
    )

# Retry logic
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
except ImportError:
    raise ImportError(
        "tenacity not installed. Install with: pip install tenacity"
    )

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Base exception for content generation errors."""
    pass


class RateLimitError(GenerationError):
    """Raised when API rate limit is exceeded."""
    pass


class ContentValidationError(GenerationError):
    """Raised when generated content fails validation."""
    pass


class ToneStyle(str, Enum):
    """Available tone styles for content generation."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    EXECUTIVE = "executive"
    FRIENDLY = "friendly"


class EmphasisType(str, Enum):
    """Content emphasis types."""
    BALANCED = "balanced"
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    IMPACT = "impact"
    CREATIVE = "creative"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class GenerationConfig:
    """Configuration for content generation."""
    
    # Model settings
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_output_tokens: int = 2048
    
    # Content settings
    hero_min_words: int = 8
    hero_max_words: int = 15
    bio_min_words: int = 150
    bio_max_words: int = 200
    project_desc_min_words: int = 80
    project_desc_max_words: int = 150
    
    # Retry settings
    max_retries: int = 3
    retry_min_wait: int = 1
    retry_max_wait: int = 10
    
    # Timeout settings
    generation_timeout: float = 30.0
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Rate limiting
    requests_per_minute: int = 60
    
    # Safety settings
    block_none_harmful: bool = True
    
    # Quality thresholds
    min_content_quality: float = 0.6


@dataclass
class CacheEntry:
    """Cache entry for generated content."""
    content: Any
    timestamp: datetime
    hits: int = 0


class ContentValidator:
    """Validates generated content quality and format."""
    
    @staticmethod
    def validate_hero_tagline(tagline: str, config: GenerationConfig) -> bool:
        """Validate hero tagline meets requirements."""
        if not tagline or not isinstance(tagline, str):
            return False
        
        # Remove quotes if present
        tagline = tagline.strip().strip('"\'')
        
        # Check word count
        word_count = len(tagline.split())
        if word_count < config.hero_min_words or word_count > config.hero_max_words:
            logger.warning(
                f"Tagline word count {word_count} outside range "
                f"[{config.hero_min_words}, {config.hero_max_words}]"
            )
            return False
        
        # Check length
        if len(tagline) < 20 or len(tagline) > 150:
            return False
        
        # Check for common issues
        if tagline.lower().startswith(('here is', 'here\'s', 'the tagline')):
            return False
        
        return True
    
    @staticmethod
    def validate_bio(bio: str, config: GenerationConfig) -> bool:
        """Validate bio meets requirements."""
        if not bio or not isinstance(bio, str):
            return False
        
        # Check word count
        word_count = len(bio.split())
        if word_count < config.bio_min_words or word_count > config.bio_max_words * 1.2:
            logger.warning(
                f"Bio word count {word_count} outside acceptable range "
                f"[{config.bio_min_words}, {config.bio_max_words * 1.2}]"
            )
            return False
        
        # Check for common issues
        if bio.lower().startswith(('here is', 'here\'s', 'the bio', 'this bio')):
            return False
        
        # Should have multiple sentences
        if bio.count('.') < 3:
            return False
        
        return True
    
    @staticmethod
    def validate_project_description(
        description: str,
        config: GenerationConfig
    ) -> bool:
        """Validate project description meets requirements."""
        if not description or not isinstance(description, str):
            return False
        
        # Check word count
        word_count = len(description.split())
        if word_count < config.project_desc_min_words * 0.8:
            logger.warning(f"Project description too short: {word_count} words")
            return False
        
        # Check for common issues
        if description.lower().startswith(('here is', 'here\'s', 'the description')):
            return False
        
        return True
    
    @staticmethod
    def calculate_quality_score(content: str, content_type: str) -> float:
        """Calculate quality score for generated content."""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Length check (30%)
        word_count = len(content.split())
        if content_type == 'hero':
            if 8 <= word_count <= 15:
                score += 0.3
        elif content_type == 'bio':
            if 150 <= word_count <= 250:
                score += 0.3
        elif content_type == 'project':
            if 80 <= word_count <= 180:
                score += 0.3
        
        # Sentence structure (20%)
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if len(sentences) >= 2:
            score += 0.2
        
        # Diversity (20%)
        words = content.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        score += unique_ratio * 0.2
        
        # No filler phrases (30%)
        filler_phrases = [
            'here is', 'here\'s', 'the following', 'as follows',
            'this is', 'let me', 'i will'
        ]
        has_filler = any(phrase in content.lower() for phrase in filler_phrases)
        if not has_filler:
            score += 0.3
        
        return min(1.0, score)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self._lock:
            now = datetime.utcnow()
            
            # Remove requests older than 1 minute
            self.requests = [
                req_time for req_time in self.requests
                if now - req_time < timedelta(minutes=1)
            ]
            
            # Check if we can make a request
            if len(self.requests) >= self.requests_per_minute:
                # Calculate wait time
                oldest = self.requests[0]
                wait_time = 60 - (now - oldest).total_seconds()
                
                if wait_time > 0:
                    logger.warning(
                        f"Rate limit reached, waiting {wait_time:.2f}s"
                    )
                    raise RateLimitError(
                        f"Rate limit exceeded. Wait {wait_time:.2f}s"
                    )
            
            # Add this request
            self.requests.append(now)


class ContentCache:
    """Simple in-memory cache for generated content."""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(
            {'args': args, 'kwargs': kwargs},
            sort_keys=True,
            default=str
        )
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached content."""
        async with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if datetime.utcnow() - entry.timestamp > timedelta(seconds=self.ttl):
                del self.cache[key]
                return None
            
            # Update hits
            entry.hits += 1
            
            return entry.content
    
    async def set(self, key: str, content: Any):
        """Set cached content."""
        async with self._lock:
            self.cache[key] = CacheEntry(
                content=content,
                timestamp=datetime.utcnow()
            )
    
    async def clear(self):
        """Clear all cache."""
        async with self._lock:
            self.cache.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_hits = sum(entry.hits for entry in self.cache.values())
            return {
                'size': len(self.cache),
                'total_hits': total_hits,
                'entries': [
                    {
                        'key': key[:16] + '...',
                        'hits': entry.hits,
                        'age_seconds': (datetime.utcnow() - entry.timestamp).total_seconds()
                    }
                    for key, entry in list(self.cache.items())[:10]
                ]
            }


class ContentGenerator:
    """
    Production-ready AI-powered content generator using Google Gemini.
    
    Features:
    - Comprehensive error handling and retries
    - Content validation and quality scoring
    - Caching for performance
    - Rate limiting
    - Safety filters
    - Detailed logging and metrics
    """
    
    def __init__(self, config: Optional[Union[Dict[str, Any], GenerationConfig]] = None):
        """
        Initialize content generator with Gemini configuration.
        
        Args:
            config: Configuration dict or GenerationConfig instance
            
        Raises:
            ValueError: If API key is not found
            GenerationError: If initialization fails
        """
        # Parse config
        if isinstance(config, dict):
            self.config = GenerationConfig(**config)
        elif isinstance(config, GenerationConfig):
            self.config = config
        else:
            self.config = GenerationConfig()
        
        # Get API key
        self.api_key = os.getenv('GEMINI_API_KEY') or self.config.__dict__.get('gemini_api_key')
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as environment variable or in config."
            )
        
        # Initialize Gemini Client (new google.genai API)
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise GenerationError(f"Failed to initialize Gemini client: {str(e)}") from e
        
        # Safety settings (new API uses types.SafetySetting)
        if self.config.block_none_harmful:
            self.safety_settings = [
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
            ]
        else:
            self.safety_settings = [
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE
                ),
            ]
        
        # Store model name and config for use in generation
        self.model_name = self.config.model_name
        self.generation_config = types.GenerationConfig(
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_output_tokens=self.config.max_output_tokens,
        )
        
        # Initialize components
        self.validator = ContentValidator()
        self.rate_limiter = RateLimiter(self.config.requests_per_minute)
        self.cache = ContentCache(self.config.cache_ttl) if self.config.enable_cache else None
        
        # Metrics
        self._generation_count = 0
        self._cache_hits = 0
        self._validation_failures = 0
        
        logger.info(
            "ContentGenerator initialized with model=%s, temperature=%.2f",
            self.config.model_name,
            self.config.temperature
        )
    
    async def _generate_content_async(self, prompt: str) -> str:
        """
        Helper method to generate content using the new google.genai API.
        
        Args:
            prompt: Text prompt to send to the model
            
        Returns:
            Generated text as string
            
        Raises:
            GenerationError: If generation fails
        """
        try:
            # Create content parts
            contents = [types.Part.from_text(prompt)]
            
            # Generate content using the new API
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract text from response
            if not response or not response.candidates:
                raise GenerationError("No response from Gemini")
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise GenerationError("Empty content in response")
            
            text_part = candidate.content.parts[0]
            if not hasattr(text_part, 'text') or not text_part.text:
                raise GenerationError("No text in response")
            
            return text_part.text
            
        except Exception as e:
            raise GenerationError(f"Content generation failed: {str(e)}") from e
    
    async def generate(
        self,
        schema: Dict[str, Any],
        user_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main generation method - creates complete portfolio content.
        
        Args:
            schema: Portfolio schema from SchemaBuilder
            user_data: Original preprocessed user data for context
            preferences: Optional user preferences for generation
            
        Returns:
            Complete portfolio with all generated content
            
        Raises:
            GenerationError: If generation fails
            ValidationError: If generated content fails validation
        """
        try:
            logger.info("Starting content generation with Gemini")
            start_time = datetime.utcnow()
            
            preferences = preferences or {}
            portfolio = {}
            
            # Generate hero section
            portfolio['hero'] = await self._generate_hero_safe(
                schema.get('hero', {}),
                user_data,
                schema.get('domain', 'software_engineering'),
                preferences
            )
            logger.info("✓ Hero section generated")
            
            # Generate bio
            portfolio['bio'] = await self._generate_bio_safe(
                schema.get('bio', {}),
                user_data,
                schema.get('domain', 'software_engineering'),
                preferences
            )
            logger.info("✓ Bio generated")
            
            # Generate/enhance projects
            portfolio['projects'] = await self._generate_projects_safe(
                schema.get('projects', []),
                user_data,
                preferences
            )
            logger.info("✓ Projects enhanced")
            
            # Include skills as-is (already structured)
            portfolio['skills'] = schema.get('skills', [])
            
            # Include experience and education
            portfolio['experience'] = user_data.get('experience', [])
            portfolio['education'] = user_data.get('education', [])
            
            # Include layout hints and theme
            portfolio['layout'] = schema.get('layout_hints', {})
            portfolio['theme'] = schema.get('theme_suggestions', {})
            
            # Add generation metadata
            duration = (datetime.utcnow() - start_time).total_seconds()
            portfolio['metadata'] = {
                'generation_duration': round(duration, 3),
                'model': self.config.model_name,
                'temperature': self.config.temperature,
                'generated_sections': ['hero', 'bio', 'projects']
            }
            
            logger.info(
                "Content generation completed successfully in %.3fs",
                duration
            )
            return portfolio
            
        except Exception as e:
            logger.error("Error in content generation: %s", str(e), exc_info=True)
            raise GenerationError(f"Content generation failed: {str(e)}") from e
    
    async def _generate_hero_safe(
        self,
        hero_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate hero section with validation and retries."""
        
        # Check cache
        cache_key = None
        if self.cache:
            cache_key = self.cache._generate_key(
                'hero',
                hero_schema.get('name'),
                domain,
                tuple(user_data.get('skills', [])[:5])
            )
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info("Hero section retrieved from cache")
                self._cache_hits += 1
                return cached
        
        # Generate with retries
        for attempt in range(self.config.max_retries):
            try:
                hero = await self._generate_hero(
                    hero_schema,
                    user_data,
                    domain,
                    preferences
                )
                
                # Validate
                if not self.validator.validate_hero_tagline(
                    hero['tagline'],
                    self.config
                ):
                    if attempt < self.config.max_retries - 1:
                        logger.warning(
                            "Hero tagline validation failed, retrying (attempt %d/%d)",
                            attempt + 1,
                            self.config.max_retries
                        )
                        await asyncio.sleep(1)
                        continue
                    else:
                        self._validation_failures += 1
                        raise ContentValidationError(
                            f"Hero tagline validation failed after {self.config.max_retries} attempts"
                        )
                
                # Cache if valid
                if self.cache and cache_key:
                    await self.cache.set(cache_key, hero)
                
                self._generation_count += 1
                return hero
                
            except (RateLimitError, asyncio.TimeoutError):
                raise
            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    logger.warning(
                        "Hero generation failed, retrying: %s",
                        str(e)
                    )
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
        
        raise GenerationError("Hero generation failed after all retries")
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _generate_hero(
        self,
        hero_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate hero section with compelling tagline."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        skills = user_data.get('skills', [])[:5]
        projects = user_data.get('projects', [])
        tone = preferences.get('tone', ToneStyle.PROFESSIONAL.value)
        
        prompt = f"""Generate a compelling hero tagline for a {domain.replace('_', ' ')}'s portfolio.

Context:
- Name: {hero_schema.get('name', 'Professional')}
- Top Skills: {', '.join(skills) if skills else 'Various technical skills'}
- Number of projects: {len(projects)}
- Desired tone: {tone}

Requirements:
- Exactly {self.config.hero_min_words}-{self.config.hero_max_words} words
- Impactful and memorable
- Specific to their expertise in {domain.replace('_', ' ')}
- NO clichés like "passionate", "problem solver", "innovative"
- Action-oriented with strong verbs
- NO introductory phrases like "Here is" or "The tagline"

Template inspiration: {hero_schema.get('template', 'Professional with expertise in domain')}

Return ONLY the tagline text, nothing else."""
        
        try:
            # Generate with timeout
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            tagline = response.strip().strip('"\'')
            
            # Clean up common issues
            tagline = self._clean_tagline(tagline)
            
            return {
                'name': hero_schema.get('name', 'Portfolio'),
                'tagline': tagline,
                'title': hero_schema.get('title', ''),
                'email': hero_schema.get('email'),
                'phone': hero_schema.get('phone'),
                'location': hero_schema.get('location'),
                'links': hero_schema.get('links', {})
            }
            
        except asyncio.TimeoutError:
            logger.error("Hero generation timed out")
            raise
        except Exception as e:
            logger.error("Hero generation error: %s", str(e))
            raise GenerationError(f"Failed to generate hero: {str(e)}") from e
    
    def _clean_tagline(self, tagline: str) -> str:
        """Clean and normalize tagline."""
        # Remove common prefixes
        prefixes_to_remove = [
            'here is the tagline:',
            'here is:',
            'tagline:',
            'the tagline is:',
        ]
        
        tagline_lower = tagline.lower()
        for prefix in prefixes_to_remove:
            if tagline_lower.startswith(prefix):
                tagline = tagline[len(prefix):].strip()
                break
        
        # Remove quotes
        tagline = tagline.strip('"\'')
        
        # Capitalize first letter
        if tagline:
            tagline = tagline[0].upper() + tagline[1:]
        
        return tagline
    
    async def _generate_bio_safe(
        self,
        bio_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Generate bio with validation and retries."""
        
        # Check cache
        cache_key = None
        if self.cache:
            cache_key = self.cache._generate_key(
                'bio',
                tuple(bio_schema.get('key_points', [])[:5]),
                domain
            )
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info("Bio retrieved from cache")
                self._cache_hits += 1
                return cached
        
        # Generate with retries
        for attempt in range(self.config.max_retries):
            try:
                bio = await self._generate_bio(
                    bio_schema,
                    user_data,
                    domain,
                    preferences
                )
                
                # Validate
                if not self.validator.validate_bio(bio, self.config):
                    if attempt < self.config.max_retries - 1:
                        logger.warning(
                            "Bio validation failed, retrying (attempt %d/%d)",
                            attempt + 1,
                            self.config.max_retries
                        )
                        await asyncio.sleep(1)
                        continue
                    else:
                        self._validation_failures += 1
                        logger.warning(
                            "Bio validation failed after retries, using anyway"
                        )
                
                # Cache if valid
                if self.cache and cache_key:
                    await self.cache.set(cache_key, bio)
                
                self._generation_count += 1
                return bio
                
            except (RateLimitError, asyncio.TimeoutError):
                raise
            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    logger.warning("Bio generation failed, retrying: %s", str(e))
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
        
        raise GenerationError("Bio generation failed after all retries")
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _generate_bio(
        self,
        bio_schema: Dict[str, Any],
        user_data: Dict[str, Any],
        domain: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Generate professional bio following the schema structure."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        key_points = bio_schema.get('key_points', [])
        tone = preferences.get('tone', ToneStyle.PROFESSIONAL.value)
        emphasis = preferences.get('emphasis', EmphasisType.BALANCED.value)
        
        # Build context from user data
        skills_context = ', '.join(user_data.get('skills', [])[:7])
        projects_count = len(user_data.get('projects', []))
        experience_count = len(user_data.get('experience', []))
        
        prompt = f"""Write a professional bio for a {domain.replace('_', ' ')}'s portfolio.

Context:
{chr(10).join(f'- {point}' for point in key_points) if key_points else '- Experienced professional in ' + domain.replace('_', ' ')}
- Key skills: {skills_context}
- {projects_count} notable projects
- {experience_count} professional experiences

Tone: {tone}
Emphasis: {emphasis}

Structure to follow (but make it flow naturally):
1. Opening hook (1 engaging sentence about who they are)
2. Background (1-2 sentences about their professional journey)
3. Expertise (2 sentences highlighting what they excel at)
4. Passion/Motivation (1 sentence about what drives them)
5. Current focus (1 sentence about what they're working on or interested in)

Requirements:
- {self.config.bio_min_words}-{self.config.bio_max_words} words total
- {tone} but engaging tone
- Natural, conversational flow - NO robotic listing
- First person voice ("I" statements)
- NO buzzwords: avoid "passionate", "innovative", "dynamic", "cutting-edge"
- NO meta-commentary like "Here is the bio" or "This bio"
- Make it sound like a real person wrote it
- Emphasize {emphasis} aspects

Return ONLY the bio paragraph, no formatting, headers, or meta-text."""
        
        try:
            # Generate with timeout
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            bio = response.strip()
            
            # Clean up
            bio = self._clean_bio(bio)
            
            return bio
            
        except asyncio.TimeoutError:
            logger.error("Bio generation timed out")
            raise
        except Exception as e:
            logger.error("Bio generation error: %s", str(e))
            raise GenerationError(f"Failed to generate bio: {str(e)}") from e
    
    def _clean_bio(self, bio: str) -> str:
        """Clean and normalize bio."""
        # Remove common prefixes
        prefixes_to_remove = [
            'here is the bio:',
            'here is:',
            'bio:',
            'the bio is:',
            'here\'s the bio:',
        ]
        
        bio_lower = bio.lower()
        for prefix in prefixes_to_remove:
            if bio_lower.startswith(prefix):
                bio = bio[len(prefix):].strip()
                break
        
        # Remove markdown formatting if present
        bio = bio.replace('**', '').replace('*', '')
        
        # Ensure proper spacing
        bio = ' '.join(bio.split())
        
        return bio
    
    async def _generate_projects_safe(
        self,
        projects_schema: List[Dict[str, Any]],
        user_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate/enhance projects with error handling."""
        enhanced_projects = []
        
        for idx, project in enumerate(projects_schema):
            try:
                if project.get('needs_enhancement'):
                    enhanced_desc = await self._enhance_project_description_safe(
                        project.get('title', f'Project {idx + 1}'),
                        project.get('raw_description', ''),
                        project.get('tech_stack', []),
                        project.get('target_length', 'medium'),
                        preferences
                    )
                else:
                    enhanced_desc = project.get('raw_description', '')
                
                enhanced_projects.append({
                    'id': project.get('id', f'project_{idx}'),
                    'title': project.get('title', f'Project {idx + 1}'),
                    'description': enhanced_desc,
                    'technologies': project.get('tech_stack', []),
                    'links': project.get('links', {}),
                    'featured': project.get('featured', False),
                    'duration': project.get('duration'),
                    'role': project.get('role')
                })
                
            except Exception as e:
                logger.error(
                    "Failed to enhance project '%s': %s",
                    project.get('title', f'Project {idx}'),
                    str(e)
                )
                # Use original description on error
                enhanced_projects.append({
                    'id': project.get('id', f'project_{idx}'),
                    'title': project.get('title', f'Project {idx + 1}'),
                    'description': project.get('raw_description', ''),
                    'technologies': project.get('tech_stack', []),
                    'links': project.get('links', {}),
                    'featured': project.get('featured', False),
                    'duration': project.get('duration'),
                    'role': project.get('role')
                })
        
        return enhanced_projects
    
    async def _enhance_project_description_safe(
        self,
        title: str,
        raw_description: str,
        tech_stack: List[str],
        target_length: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Enhance project description with validation and retries."""
        
        # Check cache
        cache_key = None
        if self.cache:
            cache_key = self.cache._generate_key(
                'project',
                title,
                raw_description[:100],
                tuple(tech_stack[:5])
            )
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info("Project description retrieved from cache")
                self._cache_hits += 1
                return cached
        
        # Generate with retries
        for attempt in range(self.config.max_retries):
            try:
                enhanced = await self._enhance_project_description(
                    title,
                    raw_description,
                    tech_stack,
                    target_length,
                    preferences
                )
                
                # Validate
                if not self.validator.validate_project_description(
                    enhanced,
                    self.config
                ):
                    if attempt < self.config.max_retries - 1:
                        logger.warning(
                            "Project description validation failed for '%s', retrying",
                            title
                        )
                        await asyncio.sleep(1)
                        continue
                    else:
                        logger.warning(
                            "Project description validation failed for '%s', using original",
                            title
                        )
                        return raw_description
                
                # Cache if valid
                if self.cache and cache_key:
                    await self.cache.set(cache_key, enhanced)
                
                self._generation_count += 1
                return enhanced
                
            except (RateLimitError, asyncio.TimeoutError):
                raise
            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    logger.warning(
                        "Project enhancement failed for '%s', retrying: %s",
                        title,
                        str(e)
                    )
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error(
                    "Project enhancement failed for '%s', using original: %s",
                    title,
                    str(e)
                )
                return raw_description
        
        return raw_description
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _enhance_project_description(
        self,
        title: str,
        raw_description: str,
        tech_stack: List[str],
        target_length: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Enhance a single project description."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        emphasis = preferences.get('emphasis', EmphasisType.TECHNICAL.value)
        
        # Map target length to word counts
        length_map = {
            'short': '80-100',
            'medium': '100-130',
            'long': '130-160'
        }
        word_range = length_map.get(target_length, '100-130')
        
        prompt = f"""Enhance this project description for a professional portfolio.

Project Title: {title}
Original Description: {raw_description}
Technologies: {', '.join(tech_stack) if tech_stack else 'Not specified'}

Requirements:
- Word count: {word_range} words
- Make it more engaging and impactful
- Emphasize {emphasis} aspects
- Highlight the problem solved and the solution
- Include technical achievements and impact (metrics if possible)
- Mention technologies naturally in context
- Use active, strong verbs (built, developed, implemented, designed)
- Stay truthful to the original description - NO fabrication
- NO introductory phrases like "Here is" or "The description"
- Make it sound professional but not robotic

Return ONLY the enhanced description, no additional commentary."""
        
        try:
            # Generate with timeout
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            enhanced = response.strip()
            
            # Clean up
            enhanced = self._clean_description(enhanced)
            
            return enhanced
            
        except asyncio.TimeoutError:
            logger.error("Project description enhancement timed out for '%s'", title)
            raise
        except Exception as e:
            logger.error("Project description enhancement error for '%s': %s", title, str(e))
            raise GenerationError(f"Failed to enhance project description: {str(e)}") from e
    
    def _clean_description(self, description: str) -> str:
        """Clean and normalize project description."""
        # Remove common prefixes
        prefixes_to_remove = [
            'here is the enhanced description:',
            'here is:',
            'enhanced description:',
            'the description is:',
        ]
        
        desc_lower = description.lower()
        for prefix in prefixes_to_remove:
            if desc_lower.startswith(prefix):
                description = description[len(prefix):].strip()
                break
        
        # Remove markdown
        description = description.replace('**', '').replace('*', '')
        
        # Ensure proper spacing
        description = ' '.join(description.split())
        
        return description
    
    async def regenerate_section(
        self,
        section: str,
        context: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Regenerate a specific section with new preferences.
        
        Args:
            section: Section name to regenerate
            context: Context for regeneration
            preferences: User preferences
            
        Returns:
            Regenerated content
            
        Raises:
            ValueError: If section is unknown
            GenerationError: If regeneration fails
        """
        try:
            preferences = preferences or {}
            
            logger.info("Regenerating section: %s", section)
            
            if section == 'hero' or section == 'hero.tagline':
                return await self._regenerate_hero(context, preferences)
            elif section == 'bio':
                return await self._regenerate_bio(context, preferences)
            elif 'project' in section:
                return await self._regenerate_project(context, preferences)
            else:
                raise ValueError(f"Unknown section for regeneration: {section}")
                
        except Exception as e:
            logger.error("Failed to regenerate section '%s': %s", section, str(e))
            raise GenerationError(f"Section regeneration failed: {str(e)}") from e
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _regenerate_hero(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate hero tagline with preferences."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        tone = preferences.get('tone', ToneStyle.PROFESSIONAL.value)
        style = preferences.get('style', 'action-oriented')
        avoid = preferences.get('avoid', [])
        
        user_profile = context.get('user_profile', {})
        current_tagline = context.get('current_content', {}).get('tagline', '')
        
        avoid_str = ', '.join(avoid) if avoid else 'none specified'
        
        prompt = f"""Generate an alternative hero tagline that's different from the current one.

Current Tagline: {current_tagline}

Context:
- Name: {user_profile.get('name', 'Professional')}
- Skills: {', '.join(user_profile.get('skills', [])[:5])}
- Title: {user_profile.get('title', '')}

Preferences:
- Tone: {tone}
- Style: {style}
- Phrases to avoid: {avoid_str}

Requirements:
- {self.config.hero_min_words}-{self.config.hero_max_words} words
- Significantly different from current tagline
- Match the {tone} tone
- {style} style
- NO clichés
- NO introductory phrases

Return ONLY the new tagline."""
        
        try:
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            new_tagline = self._clean_tagline(response.strip())
            
            # Validate
            if not self.validator.validate_hero_tagline(new_tagline, self.config):
                raise ContentValidationError("Generated tagline failed validation")
            
            self._generation_count += 1
            
            return {
                'name': user_profile.get('name'),
                'tagline': new_tagline,
                'email': user_profile.get('email'),
                'title': user_profile.get('title')
            }
            
        except asyncio.TimeoutError:
            logger.error("Hero regeneration timed out")
            raise
        except Exception as e:
            logger.error("Hero regeneration error: %s", str(e))
            raise
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _regenerate_bio(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> str:
        """Regenerate bio with different emphasis."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        emphasis = preferences.get('emphasis', EmphasisType.BALANCED.value)
        length = preferences.get('length', 'medium')
        tone = preferences.get('tone', ToneStyle.PROFESSIONAL.value)
        
        current_bio = context.get('current_content', '')
        user_profile = context.get('user_profile', {})
        existing_tone = context.get('existing_tone', 'professional')
        
        length_map = {
            'short': '100-130',
            'medium': '150-200',
            'long': '220-280'
        }
        
        word_range = length_map.get(length, '150-200')
        
        prompt = f"""Rewrite this bio with a different emphasis while keeping core facts.

Current Bio: {current_bio}

User Context:
- Name: {user_profile.get('name')}
- Skills: {', '.join(user_profile.get('skills', [])[:7])}
- Current tone: {existing_tone}

New Preferences:
- Emphasis: {emphasis} (focus more on these aspects)
- Tone: {tone}
- Length: {word_range} words

Requirements:
- Keep all factual information accurate
- Adjust emphasis to highlight {emphasis} aspects more
- Match {tone} tone
- Natural, engaging writing
- First person voice
- NO buzzwords
- NO meta-commentary

Return ONLY the rewritten bio."""
        
        try:
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            new_bio = self._clean_bio(response.strip())
            
            # Validate
            if not self.validator.validate_bio(new_bio, self.config):
                logger.warning("Regenerated bio failed validation, using anyway")
            
            self._generation_count += 1
            
            return new_bio
            
        except asyncio.TimeoutError:
            logger.error("Bio regeneration timed out")
            raise
        except Exception as e:
            logger.error("Bio regeneration error: %s", str(e))
            raise
    
    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def _regenerate_project(
        self,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate project description with preferences."""
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        emphasis = preferences.get('emphasis', EmphasisType.TECHNICAL.value)
        length = preferences.get('length', 'medium')
        
        current_project = context.get('current_content', {})
        
        length_map = {
            'short': '80-100',
            'medium': '100-130',
            'long': '130-160'
        }
        
        word_range = length_map.get(length, '100-130')
        
        prompt = f"""Rewrite this project description with a different emphasis.

Project: {current_project.get('title', 'Project')}
Current Description: {current_project.get('description', '')}
Technologies: {', '.join(current_project.get('technologies', []))}

Preferences:
- Emphasis: {emphasis}
- Length: {word_range} words

Requirements:
- Adjust focus to emphasize {emphasis} aspects
- Keep technical accuracy
- Use strong action verbs
- NO fabrication
- NO meta-commentary

Return ONLY the new description."""
        
        try:
            response = await asyncio.wait_for(
                self._generate_content_async(prompt),
                timeout=self.config.generation_timeout
            )
            
            if not response:
                raise GenerationError("Empty response from model")
            
            new_description = self._clean_description(response.strip())
            
            self._generation_count += 1
            
            return {
                **current_project,
                'description': new_description
            }
            
        except asyncio.TimeoutError:
            logger.error("Project regeneration timed out")
            raise
        except Exception as e:
            logger.error("Project regeneration error: %s", str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the content generator.
        
        Returns:
            Health status and metrics
        """
        try:
            # Try a simple generation to test API
            test_prompt = "Say 'OK' if you can respond."
            
            response = await asyncio.wait_for(
                self._generate_content_async(test_prompt),
                timeout=10.0
            )
            
            api_status = 'ok' if response else 'error'
            
        except Exception as e:
            api_status = 'error'
            logger.error("Health check failed: %s", str(e))
        
        # Get cache stats
        cache_stats = None
        if self.cache:
            cache_stats = await self.cache.get_stats()
        
        return {
            'status': api_status,
            'model': self.config.model_name,
            'api_configured': bool(self.api_key),
            'cache_enabled': self.config.enable_cache,
            'cache_stats': cache_stats,
            'metrics': {
                'total_generations': self._generation_count,
                'cache_hits': self._cache_hits,
                'validation_failures': self._validation_failures,
                'cache_hit_rate': (
                    self._cache_hits / (self._generation_count + self._cache_hits)
                    if (self._generation_count + self._cache_hits) > 0
                    else 0.0
                )
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get generation metrics."""
        return {
            'total_generations': self._generation_count,
            'cache_hits': self._cache_hits,
            'validation_failures': self._validation_failures,
            'cache_hit_rate': (
                self._cache_hits / (self._generation_count + self._cache_hits)
                if (self._generation_count + self._cache_hits) > 0
                else 0.0
            )
        }
    
    async def clear_cache(self):
        """Clear the generation cache."""
        if self.cache:
            await self.cache.clear()
            logger.info("Cache cleared")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ContentGenerator(model={self.config.model_name}, "
            f"temperature={self.config.temperature}, "
            f"generations={self._generation_count})"
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def test_generator():
        """Test the content generator."""
        
        # Create configuration
        config = GenerationConfig(
            model_name="gemini-1.5-pro",
            temperature=0.7,
            max_retries=2,
            enable_cache=True
        )
        
        # Initialize generator
        try:
            generator = ContentGenerator(config)
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please set GEMINI_API_KEY environment variable")
            return
        
        # Sample schema
        schema = {
            'domain': 'software_engineering',
            'hero': {
                'name': 'Alice Johnson',
                'email': 'alice@example.com',
                'title': 'Full-Stack Developer',
                'template': 'Building scalable solutions'
            },
            'bio': {
                'key_points': [
                    '5+ years of experience in full-stack development',
                    'Specialized in React, Node.js, and AWS',
                    'Led team of 4 developers on major projects',
                    'Passionate about clean code and user experience'
                ]
            },
            'projects': [
                {
                    'id': 'proj_1',
                    'title': 'E-commerce Platform',
                    'raw_description': 'Built online shopping platform with React and Node.js',
                    'tech_stack': ['React', 'Node.js', 'PostgreSQL', 'Redis'],
                    'needs_enhancement': True,
                    'target_length': 'medium',
                    'featured': True
                }
            ],
            'skills': ['React', 'Node.js', 'Python', 'AWS', 'Docker']
        }
        
        # Sample user data
        user_data = {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'skills': ['React', 'Node.js', 'Python', 'AWS', 'Docker', 'PostgreSQL'],
            'projects': [
                {
                    'title': 'E-commerce Platform',
                    'description': 'Built online shopping platform'
                }
            ],
            'experience': [],
            'education': []
        }
        
        print("\n" + "="*60)
        print("TESTING CONTENT GENERATOR")
        print("="*60 + "\n")
        
        try:
            # Test health check
            print("Running health check...")
            health = await generator.health_check()
            print(f"Health Status: {health['status']}\n")
            
            if health['status'] != 'ok':
                print("❌ API not responding properly")
                return
            
            # Generate content
            print("Generating portfolio content...")
            portfolio = await generator.generate(schema, user_data)
            
            print("\n" + "="*60)
            print("CONTENT GENERATED SUCCESSFULLY")
            print("="*60)
            
            # Display results
            print(f"\n📝 Hero Section:")
            print(f"   Name: {portfolio['hero']['name']}")
            print(f"   Tagline: {portfolio['hero']['tagline']}")
            
            print(f"\n📖 Bio ({len(portfolio['bio'].split())} words):")
            print(f"   {portfolio['bio'][:200]}...")
            
            print(f"\n🚀 Projects:")
            for project in portfolio['projects']:
                print(f"   - {project['title']}")
                print(f"     {project['description'][:150]}...")
            
            # Display metrics
            metrics = generator.get_metrics()
            print(f"\n📊 Metrics:")
            print(f"   Total Generations: {metrics['total_generations']}")
            print(f"   Cache Hits: {metrics['cache_hits']}")
            print(f"   Cache Hit Rate: {metrics['cache_hit_rate']:.1%}")
            
            # Test regeneration
            print("\n" + "="*60)
            print("TESTING REGENERATION")
            print("="*60 + "\n")
            
            context = {
                'user_profile': {
                    'name': 'Alice Johnson',
                    'skills': schema['skills'],
                    'email': 'alice@example.com'
                },
                'current_content': portfolio['hero']
            }
            
            print("Regenerating hero tagline with creative tone...")
            new_hero = await generator.regenerate_section(
                'hero',
                context,
                {'tone': 'creative', 'style': 'bold'}
            )
            
            print(f"New Tagline: {new_hero['tagline']}")
            
            print("\n" + "="*60)
            print("ALL TESTS PASSED!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run test
    asyncio.run(test_generator())
    