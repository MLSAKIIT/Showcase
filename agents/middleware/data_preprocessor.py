<<<<<<< HEAD
# DATA_PREPROCESSOR.PY - Input Data Preprocessing Middleware
=======
"""
DATA_PREPROCESSOR.PY
====================

Input normalization middleware for agent pipeline.

Responsibilities:
- Validate minimum viable resume data
- Normalize text fields
- Deduplicate and clean skills
- Sanitize URLs and emails
- Produce deterministic, schema-safe output

This module MUST NOT:
- Call LLMs
- Perform I/O
- Mutate incoming data
"""
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5

from __future__ import annotations

import logging
import re
<<<<<<< HEAD
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urlunparse
from datetime import datetime
from dataclasses import dataclass, field
=======
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
import string
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# Logging

logger = logging.getLogger("agents.preprocessor")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Exceptions

class PreprocessingError(Exception):
    """Base exception for preprocessing failures."""


class InputValidationError(PreprocessingError):
    """Raised when resume input is invalid."""


# Preprocessor

@dataclass
class PreprocessorConfig:
    """Configuration for the data preprocessor."""
    
    # Validation settings
    min_skill_length: int = 2
    max_skill_length: int = 50
    min_description_length: int = 10
    max_description_length: int = 5000
    
    # Quality thresholds
    min_quality_score: float = 0.3
    
    # Feature flags
    strict_validation: bool = False
    auto_fix_urls: bool = True
    deduplicate_skills: bool = True
    normalize_whitespace: bool = True
    
    # Custom normalizations
    custom_skill_normalizations: Dict[str, str] = field(default_factory=dict)
    
    # URL validation
    allowed_url_schemes: Set[str] = field(default_factory=lambda: {'http', 'https'})
    blocked_domains: Set[str] = field(default_factory=set)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataPreprocessor:
    """
<<<<<<< HEAD
    Production-ready preprocessor for parsed resume data.
    
    Features:
    - Comprehensive validation with detailed error messages
    - Configurable processing rules
    - Robust error handling
    - Data sanitization and security
    - Detailed logging and metrics
    """
    
    # Enhanced email validation (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)+$'
    )
    
    # Comprehensive skill normalizations
    SKILL_NORMALIZATIONS = {
        # JavaScript ecosystem
        'js': 'JavaScript',
        'javascript': 'JavaScript',
        'ts': 'TypeScript',
        'typescript': 'TypeScript',
        'reactjs': 'React',
        'react.js': 'React',
        'vuejs': 'Vue.js',
        'vue': 'Vue.js',
        'angularjs': 'Angular',
        'nodejs': 'Node.js',
        'node': 'Node.js',
        'nextjs': 'Next.js',
        'next': 'Next.js',
        
        # Python
        'py': 'Python',
        'python3': 'Python',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        
        # Databases
        'postgresql': 'PostgreSQL',
        'postgres': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'mongo': 'MongoDB',
        'redis': 'Redis',
        
        # AI/ML
        'ml': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'dl': 'Deep Learning',
        'nlp': 'Natural Language Processing',
        'cv': 'Computer Vision',
        'tensorflow': 'TensorFlow',
        'pytorch': 'PyTorch',
        
        # Cloud
        'aws': 'Amazon Web Services',
        'gcp': 'Google Cloud Platform',
        'azure': 'Microsoft Azure',
        
        # DevOps
        'k8s': 'Kubernetes',
        'docker': 'Docker',
        'ci/cd': 'CI/CD',
        'cicd': 'CI/CD',
        
        # Other
        'html5': 'HTML5',
        'css3': 'CSS3',
        'rest': 'REST API',
        'restful': 'REST API',
        'graphql': 'GraphQL',
        'sql': 'SQL',
        'nosql': 'NoSQL',
        'git': 'Git',
    }
    
    # Common typos and corrections
    SKILL_CORRECTIONS = {
        'javasript': 'JavaScript',
        'pythom': 'Python',
        'reactt': 'React',
        'kuberenetes': 'Kubernetes',
    }
    
    def __init__(self, config: Optional[PreprocessorConfig] = None):
        """Initialize preprocessor with configuration."""
        self.config = config or PreprocessorConfig()
        
        # Merge custom normalizations
        self.skill_normalizations = {
            **self.SKILL_NORMALIZATIONS,
            **self.config.custom_skill_normalizations
        }
        
        self._validation_warnings: List[str] = []
        self._processing_metrics: Dict[str, Any] = {}
        
        logger.info("DataPreprocessor initialized with config: %s", self.config)
    
    async def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main preprocessing method with comprehensive error handling.
        
        Args:
            raw_data: Raw data from OCR + NLP parsing
        
        Returns:
            Clean, validated, normalized data
            
        Raises:
            ValidationError: If data fails validation and strict_validation is True
        """
        start_time = datetime.utcnow()
        self._validation_warnings.clear()
        
        try:
            logger.info("Starting data preprocessing for resume")
            
            # Input validation
            if not isinstance(raw_data, dict):
                raise ValidationError(f"Expected dict, got {type(raw_data)}")
            
            if not raw_data:
                raise ValidationError("Empty data provided")
            
            # Validate required fields
            self._validate_required_fields(raw_data)
            
            # Build preprocessed data structure
            preprocessed = {
                'name': self._clean_name(raw_data.get('name', '')),
                'email': self._validate_email(raw_data.get('email', '')),
                'phone': self._clean_phone(raw_data.get('phone', '')),
                'location': self._clean_location(raw_data.get('location', '')),
                'summary': self._clean_text(raw_data.get('summary', raw_data.get('bio', ''))),
                'skills': self._process_skills(raw_data.get('skills', [])),
                'projects': self._process_projects(raw_data.get('projects', [])),
                'experience': self._process_experience(raw_data.get('experience', [])),
                'education': self._process_education(raw_data.get('education', [])),
                'certifications': self._process_certifications(raw_data.get('certifications', [])),
                'links': self._process_links(raw_data.get('links', {})),
                'metadata': self._build_metadata(raw_data, start_time)
            }
            
            # Calculate data quality score
            quality_score = self._calculate_quality_score(preprocessed)
            preprocessed['metadata']['data_quality_score'] = quality_score
            preprocessed['metadata']['validation_warnings'] = self._validation_warnings.copy()
            
            # Check quality threshold
            if self.config.strict_validation and quality_score < self.config.min_quality_score:
                raise ValidationError(
                    f"Data quality score {quality_score:.2f} below minimum threshold "
                    f"{self.config.min_quality_score:.2f}"
                )
            
            # Log processing metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                "Preprocessing complete. Quality score: %.2f, Processing time: %.3fs, Warnings: %d",
                quality_score, processing_time, len(self._validation_warnings)
            )
            
            return preprocessed
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error("Unexpected error in preprocessing: %s", str(e), exc_info=True)
            raise ValidationError(f"Preprocessing failed: {str(e)}") from e
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Validate that required fields are present with proper types.
        
        Raises:
            ValidationError: If required fields are missing or invalid
        """
        errors = []
        
        # Must have identifying information
        if not data.get('name') and not data.get('email'):
            errors.append("Missing required field: either 'name' or 'email' must be provided")
        
        # Must have some content
        content_fields = ['skills', 'projects', 'experience', 'education', 'summary']
        has_content = any(data.get(field) for field in content_fields)
        
        if not has_content:
            errors.append(
                f"Resume must contain at least one of: {', '.join(content_fields)}"
            )
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def _clean_name(self, name: str) -> str:
        """
        Clean and normalize name with enhanced validation.
        
        Args:
            name: Raw name string
            
        Returns:
            Cleaned name or default
        """
        if not name or not isinstance(name, str):
            self._validation_warnings.append("Missing or invalid name")
            return "Portfolio"
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove unwanted characters but keep international characters
        allowed = string.ascii_letters + string.whitespace + "-'.," + "àáâäãåèéêëìíîïòóôöõùúûüýÿñçčšžÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑßÇŒÆČŠŽ∂ð"
        name = ''.join(c for c in name if c in allowed)
        
        # Title case with special handling for prefixes
        words = name.split()
        lowercase_words = {'van', 'von', 'de', 'del', 'la', 'le', 'da', 'di'}
        words = [
            word.lower() if word.lower() in lowercase_words else word.title()
            for word in words
        ]
        name = ' '.join(words)
        
        # Validate length
        if len(name) < 2:
            self._validation_warnings.append(f"Name too short: '{name}'")
            return "Portfolio"
        
        if len(name) > 100:
            self._validation_warnings.append(f"Name too long, truncating: '{name}'")
            name = name[:100]
        
        return name.strip()
    
    def _validate_email(self, email: str) -> Optional[str]:
        """
        Validate and clean email address with comprehensive checks.
        
        Args:
            email: Raw email string
            
        Returns:
            Validated email or None
        """
        if not email or not isinstance(email, str):
            return None
        
        # Clean and normalize
        email = email.strip().lower()
        
        # Length validation
        if len(email) > 320:  # RFC 5321
            self._validation_warnings.append(f"Email too long: {email[:50]}...")
            return None
        
        # Pattern validation
        if not self.EMAIL_PATTERN.match(email):
            self._validation_warnings.append(f"Invalid email format: {email}")
            return None
        
        # Split and validate parts
        try:
            local, domain = email.rsplit('@', 1)
            
            if len(local) > 64 or len(domain) > 255:
                self._validation_warnings.append(f"Email parts too long: {email}")
                return None
            
            # Check for consecutive dots
            if '..' in email:
                self._validation_warnings.append(f"Invalid email (consecutive dots): {email}")
                return None
                
        except ValueError:
            self._validation_warnings.append(f"Invalid email structure: {email}")
            return None
        
        return email
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number."""
        if not phone or not isinstance(phone, str):
            return ''
        
        # Keep only digits, plus, spaces, hyphens, parentheses
        phone = re.sub(r'[^\d\s\-\+\(\)]', '', phone)
        phone = ' '.join(phone.split())
        
        return phone.strip()
    
    def _clean_location(self, location: str) -> str:
        """Clean location string."""
        if not location or not isinstance(location, str):
            return ''
        
        location = self._clean_text(location)
        return location if len(location) <= 200 else location[:200]
    
    def _process_skills(self, skills: List[Any]) -> List[str]:
        """
        Process and normalize skills with enhanced deduplication and validation.
        
        Args:
            skills: Raw skills list
            
        Returns:
            Cleaned, normalized, deduplicated skills
        """
        if not skills or not isinstance(skills, (list, tuple, set)):
            return []
        
        processed_skills = []
        seen_normalized: Set[str] = set()
        
        for skill in skills:
            try:
                # Convert to string and clean
                skill_str = str(skill).strip()
                
                # Validate length
                if len(skill_str) < self.config.min_skill_length:
                    continue
                
                if len(skill_str) > self.config.max_skill_length:
                    skill_str = skill_str[:self.config.max_skill_length]
                    self._validation_warnings.append(f"Skill truncated: {skill_str}...")
                
                # Normalize
                skill_lower = skill_str.lower()
                
                # Check for corrections first
                if skill_lower in self.SKILL_CORRECTIONS:
                    normalized = self.SKILL_CORRECTIONS[skill_lower]
                # Then check normalizations
                elif skill_lower in self.skill_normalizations:
                    normalized = self.skill_normalizations[skill_lower]
                else:
                    # Title case for consistency
                    normalized = ' '.join(word.capitalize() for word in skill_str.split())
                
                # Deduplicate
                if self.config.deduplicate_skills:
                    normalized_lower = normalized.lower()
                    if normalized_lower in seen_normalized:
                        continue
                    seen_normalized.add(normalized_lower)
                
                processed_skills.append(normalized)
                
            except Exception as e:
                logger.warning("Error processing skill '%s': %s", skill, str(e))
                continue
        
        return processed_skills
    
    def _process_projects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        """
        Process projects with comprehensive validation and structure.
        
        Args:
            projects: Raw projects list
            
        Returns:
            Structured project entries
        """
        if not projects or not isinstance(projects, (list, tuple)):
            return []
        
        processed_projects = []
        
        for idx, project in enumerate(projects, 1):
            try:
                if isinstance(project, str):
                    # Simple string project
                    description = self._clean_text(project)
                    if len(description) < self.config.min_description_length:
                        continue
                    
                    processed_project = {
                        'title': f'Project {idx}',
                        'description': description,
                        'technologies': [],
                        'links': {},
                        'highlights': []
                    }
                    
                elif isinstance(project, dict):
                    # Structured project
                    title = project.get('title', project.get('name', f'Project {idx}'))
                    description = self._clean_text(project.get('description', ''))
                    
                    # Validate description length
                    if description and len(description) < self.config.min_description_length:
                        self._validation_warnings.append(
                            f"Project '{title}' description too short, skipping"
                        )
                        continue
                    
                    if len(description) > self.config.max_description_length:
                        description = description[:self.config.max_description_length]
                        self._validation_warnings.append(f"Project '{title}' description truncated")
                    
                    processed_project = {
                        'title': self._clean_text(title),
                        'description': description,
                        'technologies': self._extract_technologies(project),
                        'links': self._process_project_links(project.get('links', {})),
                        'highlights': self._extract_highlights(project),
                        'duration': self._normalize_duration(project.get('duration', '')),
                        'role': self._clean_text(project.get('role', ''))
                    }
                else:
                    self._validation_warnings.append(
                        f"Invalid project format at index {idx}: {type(project)}"
                    )
                    continue
                
                # Only include if has meaningful content
                if processed_project.get('description') or processed_project.get('technologies'):
                    processed_projects.append(processed_project)
                    
            except Exception as e:
                logger.warning("Error processing project %d: %s", idx, str(e))
                continue
        
        return processed_projects
    
    def _process_experience(self, experience: List[Any]) -> List[Dict[str, Any]]:
        """
        Process work experience with validation.
        
        Args:
            experience: Raw experience list
            
        Returns:
            Structured experience entries
        """
        if not experience or not isinstance(experience, (list, tuple)):
=======
    Normalizes parsed resume data before agent orchestration.
    """

    EMAIL_REGEX = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    SKILL_MAP = {
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "reactjs": "React",
        "nodejs": "Node.js",
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence",
        "nlp": "Natural Language Processing",
        "cv": "Computer Vision",
        "aws": "Amazon Web Services",
        "gcp": "Google Cloud Platform",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        logger.info("DataPreprocessor initialized")

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    async def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point for preprocessing pipeline.
        """

        self._validate_minimum_input(raw_data)

        processed = {
            "name": self._clean_name(raw_data.get("name")),
            "email": self._validate_email(raw_data.get("email")),
            "skills": self._process_skills(raw_data.get("skills")),
            "projects": self._process_projects(raw_data.get("projects")),
            "experience": self._process_experience(raw_data.get("experience")),
            "education": self._process_education(raw_data.get("education")),
            "links": self._process_links(raw_data.get("links")),
            "metadata": {
                "processed_at": self._timestamp(),
                "source": raw_data.get("source", "unknown"),
                "quality_score": 0.0,
            },
        }

        processed["metadata"]["quality_score"] = self._quality_score(processed)

        logger.info(
            "Preprocessing complete | quality_score=%.2f",
            processed["metadata"]["quality_score"],
        )

        return processed

    # -----------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------

    def _validate_minimum_input(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise InputValidationError("Input must be a dictionary")

        if not data.get("name") and not data.get("email"):
            raise InputValidationError("Either name or email is required")

        if not any(data.get(k) for k in ("skills", "projects", "experience")):
            raise InputValidationError(
                "At least one of skills, projects, or experience is required"
            )

    # -----------------------------------------------------------------
    # Field processors
    # -----------------------------------------------------------------

    def _clean_name(self, name: Optional[str]) -> str:
        if not name:
            return "Portfolio"

        allowed = string.ascii_letters + " -'."
        cleaned = "".join(c for c in name if c in allowed)
        cleaned = " ".join(cleaned.split())

        return cleaned.title()

    def _validate_email(self, email: Optional[str]) -> Optional[str]:
        if not email:
            return None

        email = email.strip().lower()
        if self.EMAIL_REGEX.match(email):
            return email

        logger.warning("Invalid email dropped: %s", email)
        return None

    def _process_skills(self, skills: Any) -> List[str]:
        if not skills:
            return []

        if not isinstance(skills, list):
            skills = [skills]

        seen = set()
        output: List[str] = []

        for raw in skills:
            skill = str(raw).strip()
            if len(skill) < 2:
                continue

            key = skill.lower()
            normalized = self.SKILL_MAP.get(key, skill)

            norm_key = normalized.lower()
            if norm_key not in seen:
                seen.add(norm_key)
                output.append(normalized)

        return output

    def _process_projects(self, projects: Any) -> List[Dict[str, Any]]:
        if not projects:
            return []

        output = []

        for idx, proj in enumerate(projects if isinstance(projects, list) else []):
            if isinstance(proj, str):
                output.append({
                    "title": f"Project {idx + 1}",
                    "description": self._clean_text(proj),
                    "technologies": [],
                    "links": {},
                })
                continue

            if not isinstance(proj, dict):
                continue

            output.append({
                "title": proj.get("title") or proj.get("name") or f"Project {idx + 1}",
                "description": self._clean_text(proj.get("description")),
                "technologies": self._extract_tech(proj),
                "links": self._process_links(proj.get("links")),
            })

        return output

    def _process_experience(self, experience: Any) -> List[Dict[str, Any]]:
        if not experience:
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
            return []

        output = []

        for exp in experience if isinstance(experience, list) else []:
            if not isinstance(exp, dict):
                continue
<<<<<<< HEAD
            
            try:
                company = self._clean_text(exp.get('company', exp.get('organization', '')))
                position = self._clean_text(exp.get('position', exp.get('role', exp.get('title', ''))))
                
                # Must have company or position
                if not company and not position:
                    continue
                
                description = self._clean_text(exp.get('description', ''))
                if len(description) > self.config.max_description_length:
                    description = description[:self.config.max_description_length]
                
                processed_exp = {
                    'company': company,
                    'position': position,
                    'duration': self._normalize_duration(exp.get('duration', exp.get('period', ''))),
                    'description': description,
                    'location': self._clean_text(exp.get('location', '')),
                    'achievements': self._extract_highlights(exp),
                    'technologies': self._extract_technologies(exp)
                }
                
                processed_experience.append(processed_exp)
                
            except Exception as e:
                logger.warning("Error processing experience entry: %s", str(e))
                continue
        
        return processed_experience
    
    def _process_education(self, education: List[Any]) -> List[Dict[str, Any]]:
        """
        Process education entries with validation.
        
        Args:
            education: Raw education list
            
        Returns:
            Structured education entries
        """
        if not education or not isinstance(education, (list, tuple)):
=======

            output.append({
                "company": exp.get("company") or exp.get("organization"),
                "position": exp.get("position") or exp.get("role"),
                "duration": self._normalize_duration(exp.get("duration")),
                "description": self._clean_text(exp.get("description")),
                "location": exp.get("location"),
            })

        return output

    def _process_education(self, education: Any) -> List[Dict[str, Any]]:
        if not education:
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
            return []

        output = []

        for edu in education if isinstance(education, list) else []:
            if not isinstance(edu, dict):
                continue
<<<<<<< HEAD
            
            try:
                institution = self._clean_text(
                    edu.get('institution', edu.get('school', edu.get('university', '')))
                )
                
                if not institution:
                    continue
                
                processed_edu = {
                    'institution': institution,
                    'degree': self._clean_text(edu.get('degree', '')),
                    'field': self._clean_text(edu.get('field', edu.get('major', ''))),
                    'year': self._extract_year(edu.get('year', edu.get('graduation', ''))),
                    'gpa': self._extract_gpa(edu.get('gpa', '')),
                    'honors': self._clean_text(edu.get('honors', ''))
                }
                
                processed_education.append(processed_edu)
                
            except Exception as e:
                logger.warning("Error processing education entry: %s", str(e))
                continue
        
        return processed_education
    
    def _process_certifications(self, certifications: List[Any]) -> List[Dict[str, Any]]:
        """Process professional certifications."""
        if not certifications or not isinstance(certifications, (list, tuple)):
            return []
        
        processed_certs = []
        
        for cert in certifications:
            try:
                if isinstance(cert, str):
                    processed_certs.append({
                        'name': self._clean_text(cert),
                        'issuer': '',
                        'year': None
                    })
                elif isinstance(cert, dict):
                    processed_certs.append({
                        'name': self._clean_text(cert.get('name', cert.get('title', ''))),
                        'issuer': self._clean_text(cert.get('issuer', cert.get('organization', ''))),
                        'year': self._extract_year(cert.get('year', cert.get('date', '')))
                    })
            except Exception as e:
                logger.warning("Error processing certification: %s", str(e))
                continue
        
        return [c for c in processed_certs if c['name']]
    
    def _process_links(self, links: Dict[str, Any]) -> Dict[str, str]:
        """
        Process and validate social/portfolio links with security checks.
        
        Args:
            links: Raw links dictionary
            
        Returns:
            Validated links dictionary
        """
        if not links or not isinstance(links, dict):
            return {}
        
        processed_links = {}
        
        for key, url in links.items():
            if not url or not isinstance(url, str):
                continue
            
            try:
                # Clean and validate URL
                cleaned_url = self._validate_url(str(url))
                if cleaned_url:
                    # Normalize key
                    key_normalized = key.lower().strip().replace(' ', '_')
                    processed_links[key_normalized] = cleaned_url
            except Exception as e:
                logger.warning("Error processing link '%s': %s", key, str(e))
                continue
        
        return processed_links
    
    def _process_project_links(self, links: Any) -> Dict[str, str]:
        """Process links specific to projects with flexible input."""
        if isinstance(links, str):
            # Single URL provided
            validated = self._validate_url(links)
            return {'demo': validated} if validated else {}
        elif isinstance(links, dict):
            return self._process_links(links)
        elif isinstance(links, (list, tuple)):
            # List of URLs
            result = {}
            for idx, link in enumerate(links):
                validated = self._validate_url(str(link))
                if validated:
                    result[f'link_{idx + 1}'] = validated
            return result
        else:
            return {}
    
    def _validate_url(self, url: str) -> Optional[str]:
        """
        Validate and normalize URL with security checks.
        
        Args:
            url: Raw URL string
            
        Returns:
            Validated URL or None
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Check length
        if len(url) > 2048:
            self._validation_warnings.append(f"URL too long: {url[:50]}...")
            return None
        
        # Add https:// if no scheme
        if not url.startswith(('http://', 'https://', '//')):
            if self.config.auto_fix_urls:
                url = 'https://' + url
            else:
                self._validation_warnings.append(f"URL missing scheme: {url}")
                return None
        
        try:
            parsed = urlparse(url)
            
            # Validate scheme
            if parsed.scheme not in self.config.allowed_url_schemes:
                self._validation_warnings.append(
                    f"Invalid URL scheme '{parsed.scheme}': {url}"
                )
                return None
            
            # Validate netloc
            if not parsed.netloc:
                self._validation_warnings.append(f"Invalid URL (no domain): {url}")
                return None
            
            # Check blocked domains
            domain = parsed.netloc.lower()
            if any(blocked in domain for blocked in self.config.blocked_domains):
                self._validation_warnings.append(f"Blocked domain: {domain}")
                return None
            
            # Reconstruct clean URL
            clean_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return clean_url
            
        except Exception as e:
            self._validation_warnings.append(f"Invalid URL '{url}': {str(e)}")
            return None
    
    def _extract_technologies(self, item: Dict[str, Any]) -> List[str]:
        """
        Extract and normalize technology list from various fields.
        
        Args:
            item: Dictionary containing technology information
            
        Returns:
            List of normalized technologies
        """
        # Try multiple field names
        tech = None
        for field in ['technologies', 'tech_stack', 'tools', 'stack', 'tech']:
            if field in item:
                tech = item[field]
                break
        
        if not tech:
            return []
        
        # Handle different formats
        if isinstance(tech, str):
            # Split by common separators
            tech = re.split(r'[,;|]', tech)
            tech = [t.strip() for t in tech if t.strip()]
        elif not isinstance(tech, (list, tuple)):
            return []
        
        # Process as skills
        return self._process_skills(tech)
    
    def _extract_highlights(self, item: Dict[str, Any]) -> List[str]:
        """Extract highlights/achievements from various fields."""
        highlights = item.get('highlights', item.get('achievements', item.get('bullets', [])))
        
        if isinstance(highlights, str):
            # Split by newlines or bullet points
            highlights = re.split(r'[\n•\-\*]', highlights)
        
        if not isinstance(highlights, (list, tuple)):
            return []
        
        processed = []
        for highlight in highlights:
            cleaned = self._clean_text(str(highlight))
            if cleaned and len(cleaned) >= 10:
                processed.append(cleaned)
        
        return processed
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text content with normalization.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ''
        
        if self.config.normalize_whitespace:
            # Replace multiple whitespace with single space
            text = ' '.join(text.split())
        
        # Remove control characters but keep newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Normalize unicode
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        
        return text.strip()
    
    def _normalize_duration(self, duration: str) -> str:
        """
        Normalize duration strings with format standardization.
        
        Args:
            duration: Raw duration string
            
        Returns:
            Normalized duration
        """
        if not duration or not isinstance(duration, str):
            return ''
        
        duration = ' '.join(str(duration).split())
        
        # Standardize common patterns
        duration = re.sub(r'\s*-\s*', ' - ', duration)
        duration = re.sub(r'\bto\b', '-', duration, flags=re.IGNORECASE)
        duration = duration.replace('present', 'Present')
        duration = duration.replace('current', 'Present')
        
        return duration.strip()
    
    def _extract_year(self, year_str: Any) -> Optional[int]:
        """
        Extract year from various formats with validation.
        
        Args:
            year_str: Raw year string or number
            
        Returns:
            Year as integer or None
        """
        if not year_str:
            return None
        
        # If already an int
        if isinstance(year_str, int):
            if 1900 <= year_str <= 2100:
                return year_str
            return None
        
        # Try to extract 4-digit year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(year_str))
        if year_match:
            year = int(year_match.group())
            # Validate reasonable range
            if 1950 <= year <= 2100:
                return year
        
        return None
    
    def _extract_gpa(self, gpa_str: Any) -> Optional[float]:
        """Extract and validate GPA."""
        if not gpa_str:
            return None
        
        try:
            # Extract number
            match = re.search(r'(\d+\.?\d*)', str(gpa_str))
            if match:
                gpa = float(match.group(1))
                # Validate range (assuming 4.0 scale)
                if 0.0 <= gpa <= 4.0:
                    return round(gpa, 2)
                # Might be on different scale
                if 0.0 <= gpa <= 100.0:
                    return round(gpa, 2)
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate comprehensive data quality score (0.0 to 1.0).
        
        Factors considered:
        - Presence and completeness of key fields
        - Amount and depth of content
        - Validity of data (emails, URLs)
        - Richness of information
        
        Args:
            data: Preprocessed data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 0.0
        
        # Name (10 points)
        max_score += 10
        if data.get('name') and data['name'] != 'Portfolio':
            score += 10
        elif data.get('name'):
            score += 5
        
        # Email (10 points)
        max_score += 10
        if data.get('email'):
            score += 10
        
        # Phone (5 points)
        max_score += 5
        if data.get('phone'):
            score += 5
        
        # Location (5 points)
        max_score += 5
        if data.get('location'):
            score += 5
        
        # Summary (10 points)
        max_score += 10
        if data.get('summary'):
            summary_len = len(data['summary'])
            if summary_len >= 100:
                score += 10
            elif summary_len >= 50:
                score += 7
            elif summary_len >= 20:
                score += 4
        
        # Skills (20 points)
        max_score += 20
        skills_count = len(data.get('skills', []))
        if skills_count >= 10:
            score += 20
        elif skills_count >= 5:
            score += 15
        elif skills_count >= 1:
            score += 10
        
        # Projects (25 points)
        max_score += 25
        projects = data.get('projects', [])
        if projects:
            project_score = min(25, len(projects) * 8)
            # Bonus for detailed projects
            detailed_projects = sum(
                1 for p in projects
                if p.get('technologies') and len(p.get('description', '')) > 100
            )
            project_score += min(5, detailed_projects * 2)
            score += min(25, project_score)
        
        # Experience (20 points)
        max_score += 20
        experience = data.get('experience', [])
        if experience:
            exp_score = min(15, len(experience) * 5)
            # Bonus for detailed experience
            detailed_exp = sum(
                1 for e in experience
                if e.get('description') or e.get('achievements')
            )
            exp_score += min(5, detailed_exp * 2)
            score += min(20, exp_score)
        
        # Education (10 points)
        max_score += 10
        education = data.get('education', [])
        if education:
            score += min(10, len(education) * 5)
        
        # Certifications (5 points)
        max_score += 5
        certs = data.get('certifications', [])
        if certs:
            score += min(5, len(certs) * 2)
        
        # Links (10 points)
        max_score += 10
        links = data.get('links', {})
        if links:
            score += min(10, len(links) * 3)
        
        # Calculate final score
        final_score = score / max_score if max_score > 0 else 0.0
        
        return round(final_score, 3)
    
    def _build_metadata(self, raw_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """
        Build comprehensive metadata dictionary.
        
        Args:
            raw_data: Original raw data
            start_time: Processing start time
            
        Returns:
            Metadata dictionary
        """
        return {
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'processing_version': '2.0.0',
            'source': raw_data.get('source', 'unknown'),
            'source_format': raw_data.get('format', 'unknown'),
            'data_quality_score': 0.0,  # Will be updated
            'validation_warnings': [],  # Will be updated
            'field_counts': {
                'skills': len(raw_data.get('skills', [])),
                'projects': len(raw_data.get('projects', [])),
                'experience': len(raw_data.get('experience', [])),
                'education': len(raw_data.get('education', [])),
            },
            'config': {
                'strict_validation': self.config.strict_validation,
                'auto_fix_urls': self.config.auto_fix_urls,
            }
        }
    
    def get_validation_warnings(self) -> List[str]:
        """Get list of validation warnings from last preprocessing."""
        return self._validation_warnings.copy()
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics from last preprocessing."""
        return self._processing_metrics.copy()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = PreprocessorConfig(
        strict_validation=False,
        auto_fix_urls=True,
        min_quality_score=0.3,
        custom_skill_normalizations={
            'reactnative': 'React Native',
            'rn': 'React Native',
        }
    )
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor(config)
    
    # Example data
    sample_data = {
        'name': 'John  Doe',
        'email': 'john.doe@example.com',
        'skills': ['js', 'Python', 'react', 'PYTHON', 'aws'],
        'projects': [
            {
                'title': 'E-commerce Platform',
                'description': 'Built a full-stack e-commerce platform with React and Node.js',
                'technologies': ['React', 'Node.js', 'MongoDB'],
                'links': {'github': 'github.com/johndoe/ecommerce'}
            }
        ],
        'experience': [
            {
                'company': 'Tech Corp',
                'position': 'Software Engineer',
                'duration': '2020 - Present',
                'description': 'Developed microservices architecture'
            }
        ],
        'education': [
            {
                'institution': 'University of Technology',
                'degree': 'B.S. Computer Science',
                'year': '2020'
            }
        ]
    }
    
    # Process data
    import asyncio
    
    async def test():
        result = await preprocessor.preprocess(sample_data)
        print("\n=== PREPROCESSED DATA ===")
        print(f"Quality Score: {result['metadata']['data_quality_score']}")
        print(f"Warnings: {len(result['metadata']['validation_warnings'])}")
        print(f"\nSkills: {result['skills']}")
        print(f"Projects: {len(result['projects'])}")
        
        if result['metadata']['validation_warnings']:
            print("\n=== WARNINGS ===")
            for warning in result['metadata']['validation_warnings']:
                print(f"  - {warning}")
    
    asyncio.run(test())
=======

            output.append({
                "institution": edu.get("institution") or edu.get("school"),
                "degree": edu.get("degree"),
                "field": edu.get("field") or edu.get("major"),
                "year": self._extract_year(edu.get("year")),
            })

        return output

    def _process_links(self, links: Any) -> Dict[str, str]:
        if not isinstance(links, dict):
            return {}

        clean = {}
        for k, v in links.items():
            url = self._validate_url(v)
            if url:
                clean[k.lower()] = url

        return clean

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def _validate_url(self, url: Any) -> Optional[str]:
        if not url:
            return None

        url = str(url).strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return url
        except Exception:
            pass

        logger.warning("Invalid URL dropped: %s", url)
        return None

    def _extract_tech(self, project: Dict[str, Any]) -> List[str]:
        tech = project.get("technologies") or project.get("tools") or []
        if isinstance(tech, str):
            tech = [t.strip() for t in tech.split(",")]
        return [t for t in tech if t]

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        text = " ".join(str(text).split())
        return text.encode("ascii", "ignore").decode()

    def _normalize_duration(self, duration: Any) -> Optional[str]:
        if not duration:
            return None
        return " ".join(str(duration).split())

    def _extract_year(self, value: Any) -> Optional[int]:
        if not value:
            return None
        match = re.search(r"\b(19|20)\d{2}\b", str(value))
        return int(match.group()) if match else None

    def _quality_score(self, data: Dict[str, Any]) -> float:
        score = 0.0

        if data["name"] != "Portfolio":
            score += 0.15
        if data["email"]:
            score += 0.15
        if data["skills"]:
            score += min(0.25, len(data["skills"]) * 0.05)
        if data["projects"]:
            score += min(0.25, len(data["projects"]) * 0.1)
        if data["experience"]:
            score += 0.2

        return round(min(score, 1.0), 2)

    def _timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
