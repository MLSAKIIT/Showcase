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
"""

import logging
import re
import string
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger("agents.preprocessor")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Exceptions
class PreprocessingError(Exception):
    """Base exception for preprocessing failures."""
    pass


class InputValidationError(PreprocessingError):
    """Raised when resume input is invalid."""
    pass


# Configuration
class PreprocessorConfig:
    """Configuration for the data preprocessor."""
    
    def __init__(self):
        self.min_skill_length = 2
        self.max_skill_length = 50
        self.min_description_length = 10
        self.max_description_length = 5000
        self.min_quality_score = 0.3
        self.strict_validation = False
        self.auto_fix_urls = True
        self.deduplicate_skills = True


# Preprocessor
class DataPreprocessor:
    """
    Input normalization middleware for resume data.
    
    Validates, cleans, and normalizes parsed resume data before
    passing to schema builder and content generator.
    """
    
    # Email validation (RFC 5322 simplified)
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)+$"
    )
    
    # Skill normalizations
    SKILL_MAP = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "py": "Python",
        "python3": "Python",
        "reactjs": "React",
        "react.js": "React",
        "vuejs": "Vue.js",
        "nodejs": "Node.js",
        "node": "Node.js",
        "nextjs": "Next.js",
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "redis": "Redis",
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence",
        "dl": "Deep Learning",
        "nlp": "Natural Language Processing",
        "cv": "Computer Vision",
        "aws": "Amazon Web Services",
        "gcp": "Google Cloud Platform",
        "azure": "Microsoft Azure",
        "k8s": "Kubernetes",
        "docker": "Docker",
        "cicd": "CI/CD",
        "ci/cd": "CI/CD",
        "graphql": "GraphQL",
        "rest": "REST API",
        "sql": "SQL",
        "git": "Git",
    }
    
    def __init__(self, config: Optional[PreprocessorConfig] = None):
        """Initialize preprocessor with configuration."""
        self.config = config or PreprocessorConfig()
        self._warnings: List[str] = []
        logger.info("DataPreprocessor initialized")
    
    async def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main preprocessing method.
        
        Args:
            raw_data: Raw data from OCR + NLP parsing
        
        Returns:
            Clean, validated, normalized data
            
        Raises:
            InputValidationError: If data fails validation
        """
        self._warnings.clear()
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting data preprocessing")
            
            # Validate input
            self._validate_input(raw_data)
            
            # Process all fields
            processed = {
                'name': self._clean_name(raw_data.get('name', '')),
                'email': self._validate_email(raw_data.get('email', '')),
                'phone': self._clean_phone(raw_data.get('phone', '')),
                'location': self._clean_text(raw_data.get('location', '')),
                'summary': self._clean_text(raw_data.get('summary', raw_data.get('bio', ''))),
                'skills': self._process_skills(raw_data.get('skills', [])),
                'projects': self._process_projects(raw_data.get('projects', [])),
                'experience': self._process_experience(raw_data.get('experience', [])),
                'education': self._process_education(raw_data.get('education', [])),
                'links': self._process_links(raw_data.get('links', {})),
                'metadata': {
                    'processed_at': datetime.utcnow().isoformat() + 'Z',
                    'quality_score': 0.0,
                    'warnings': []
                }
            }
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(processed)
            processed['metadata']['quality_score'] = quality_score
            processed['metadata']['warnings'] = self._warnings
            
            # Check quality threshold
            if self.config.strict_validation and quality_score < self.config.min_quality_score:
                raise InputValidationError(
                    f"Data quality score {quality_score:.2f} below minimum "
                    f"{self.config.min_quality_score:.2f}"
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Preprocessing complete | quality_score={quality_score:.2f} | "
                f"duration={duration:.3f}s | warnings={len(self._warnings)}"
            )
            
            return processed
            
        except InputValidationError:
            raise
        except Exception as e:
            logger.error(f"Preprocessing error: {str(e)}", exc_info=True)
            raise InputValidationError(f"Preprocessing failed: {str(e)}") from e
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Validate minimum required fields."""
        if not isinstance(data, dict) or not data:
            raise InputValidationError("Input must be non-empty dictionary")
        
        # Must have identifier
        if not data.get('name') and not data.get('email'):
            raise InputValidationError("Input must contain 'name' or 'email'")
        
        # Must have content
        has_content = any([
            data.get('skills'),
            data.get('projects'),
            data.get('experience'),
            data.get('education'),
            data.get('summary')
        ])
        
        if not has_content:
            raise InputValidationError(
                "Input must contain at least one of: skills, projects, experience, education, summary"
            )
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize name."""
        if not name or not isinstance(name, str):
            self._warnings.append("Missing or invalid name")
            return "Portfolio"
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Keep letters, spaces, and common punctuation
        allowed = string.ascii_letters + string.whitespace + "-'.,"
        name = ''.join(c for c in name if c in allowed)
        
        # Title case
        name = ' '.join(word.title() for word in name.split())
        
        if len(name) < 2:
            self._warnings.append(f"Name too short: '{name}'")
            return "Portfolio"
        
        return name.strip()[:100]
    
    def _validate_email(self, email: str) -> Optional[str]:
        """Validate and clean email address."""
        if not email or not isinstance(email, str):
            return None
        
        email = email.strip().lower()
        
        # Length check
        if len(email) > 320:
            self._warnings.append("Email too long")
            return None
        
        # Pattern validation
        if not self.EMAIL_REGEX.match(email):
            self._warnings.append(f"Invalid email format: {email}")
            return None
        
        return email
    
    def _clean_phone(self, phone: str) -> str:
        """Clean phone number."""
        if not phone or not isinstance(phone, str):
            return ''
        
        # Keep only digits, plus, spaces, hyphens, parentheses
        phone = re.sub(r'[^\d\s\-\+\(\)]', '', phone)
        return ' '.join(phone.split()).strip()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ''
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    def _process_skills(self, skills: List[Any]) -> List[str]:
        """Process and normalize skills."""
        if not skills or not isinstance(skills, (list, tuple, set)):
            return []
        
        processed = []
        seen = set()
        
        for skill in skills:
            try:
                skill_str = str(skill).strip()
                
                # Validate length
                if len(skill_str) < self.config.min_skill_length:
                    continue
                
                if len(skill_str) > self.config.max_skill_length:
                    skill_str = skill_str[:self.config.max_skill_length]
                
                # Normalize
                skill_lower = skill_str.lower()
                normalized = self.SKILL_MAP.get(skill_lower, skill_str.title())
                
                # Deduplicate
                if self.config.deduplicate_skills:
                    normalized_lower = normalized.lower()
                    if normalized_lower in seen:
                        continue
                    seen.add(normalized_lower)
                
                processed.append(normalized)
                
            except Exception as e:
                logger.warning(f"Error processing skill: {str(e)}")
                continue
        
        return processed
    
    def _process_projects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        """Process projects."""
        if not projects or not isinstance(projects, (list, tuple)):
            return []
        
        processed = []
        
        for idx, project in enumerate(projects, 1):
            try:
                if isinstance(project, str):
                    desc = self._clean_text(project)
                    if len(desc) < self.config.min_description_length:
                        continue
                    
                    processed.append({
                        'title': f'Project {idx}',
                        'description': desc,
                        'technologies': [],
                        'links': {}
                    })
                    
                elif isinstance(project, dict):
                    title = project.get('title', project.get('name', f'Project {idx}'))
                    description = self._clean_text(project.get('description', ''))
                    
                    if description and len(description) >= self.config.min_description_length:
                        if len(description) > self.config.max_description_length:
                            description = description[:self.config.max_description_length]
                        
                        processed.append({
                            'title': self._clean_text(title),
                            'description': description,
                            'technologies': self._extract_technologies(project),
                            'links': self._process_links(project.get('links', {}))
                        })
                        
            except Exception as e:
                logger.warning(f"Error processing project: {str(e)}")
                continue
        
        return processed
    
    def _process_experience(self, experience: List[Any]) -> List[Dict[str, Any]]:
        """Process work experience."""
        if not experience or not isinstance(experience, (list, tuple)):
            return []
        
        processed = []
        
        for exp in experience:
            try:
                if not isinstance(exp, dict):
                    continue
                
                company = self._clean_text(exp.get('company', exp.get('organization', '')))
                position = self._clean_text(exp.get('position', exp.get('role', '')))
                
                if not company and not position:
                    continue
                
                description = self._clean_text(exp.get('description', ''))
                if len(description) > self.config.max_description_length:
                    description = description[:self.config.max_description_length]
                
                processed.append({
                    'company': company,
                    'position': position,
                    'duration': self._normalize_duration(exp.get('duration', '')),
                    'description': description,
                    'location': self._clean_text(exp.get('location', ''))
                })
                
            except Exception as e:
                logger.warning(f"Error processing experience: {str(e)}")
                continue
        
        return processed
    
    def _process_education(self, education: List[Any]) -> List[Dict[str, Any]]:
        """Process education."""
        if not education or not isinstance(education, (list, tuple)):
            return []
        
        processed = []
        
        for edu in education:
            try:
                if not isinstance(edu, dict):
                    continue
                
                institution = self._clean_text(
                    edu.get('institution', edu.get('school', edu.get('university', '')))
                )
                
                if not institution:
                    continue
                
                processed.append({
                    'institution': institution,
                    'degree': self._clean_text(edu.get('degree', '')),
                    'field': self._clean_text(edu.get('field', edu.get('major', ''))),
                    'year': self._extract_year(edu.get('year', edu.get('graduation', '')))
                })
                
            except Exception as e:
                logger.warning(f"Error processing education: {str(e)}")
                continue
        
        return processed
    
    def _process_links(self, links: Dict[str, Any]) -> Dict[str, str]:
        """Process and validate links."""
        if not links or not isinstance(links, dict):
            return {}
        
        processed = {}
        
        for key, url in links.items():
            if not url or not isinstance(url, str):
                continue
            
            try:
                validated = self._validate_url(str(url))
                if validated:
                    key_normalized = key.lower().strip().replace(' ', '_')
                    processed[key_normalized] = validated
            except Exception as e:
                logger.warning(f"Error processing link: {str(e)}")
                continue
        
        return processed
    
    def _validate_url(self, url: str) -> Optional[str]:
        """Validate and normalize URL."""
        if not url or len(url) > 2048:
            return None
        
        url = url.strip()
        
        # Add https:// if no scheme
        if not url.startswith(('http://', 'https://', '//')):
            if self.config.auto_fix_urls:
                url = 'https://' + url
            else:
                return None
        
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                self._warnings.append(f"Invalid URL: {url}")
                return None
            
            return url
            
        except Exception as e:
            logger.warning(f"URL validation error: {str(e)}")
            return None
    
    def _extract_technologies(self, item: Dict[str, Any]) -> List[str]:
        """Extract technologies from project."""
        tech = None
        for field in ['technologies', 'tech_stack', 'tools', 'stack', 'tech']:
            if field in item:
                tech = item[field]
                break
        
        if not tech:
            return []
        
        # Handle string format
        if isinstance(tech, str):
            tech = re.split(r'[,;|]', tech)
            tech = [t.strip() for t in tech if t.strip()]
        elif not isinstance(tech, (list, tuple)):
            return []
        
        return self._process_skills(tech)
    
    def _normalize_duration(self, duration: str) -> str:
        """Normalize duration string."""
        if not duration or not isinstance(duration, str):
            return ''
        
        duration = ' '.join(duration.split())
        duration = re.sub(r'\s*-\s*', ' - ', duration)
        duration = duration.replace('present', 'Present').replace('current', 'Present')
        
        return duration.strip()
    
    def _extract_year(self, year_str: Any) -> Optional[int]:
        """Extract year from string."""
        if not year_str:
            return None
        
        if isinstance(year_str, int) and 1900 <= year_str <= 2100:
            return year_str
        
        # Extract 4-digit year
        match = re.search(r'\b(19\d{2}|20\d{2})\b', str(year_str))
        if match:
            year = int(match.group())
            if 1950 <= year <= 2100:
                return year
        
        return None
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score (0.0 to 1.0)."""
        score = 0.0
        
        # Name (15%)
        if data.get('name') and data['name'] != 'Portfolio':
            score += 0.15
        
        # Email (15%)
        if data.get('email'):
            score += 0.15
        
        # Summary (10%)
        if data.get('summary') and len(data['summary']) > 50:
            score += 0.10
        
        # Skills (20%)
        skills = len(data.get('skills', []))
        score += min(0.20, skills * 0.02)
        
        # Projects (20%)
        projects = len(data.get('projects', []))
        score += min(0.20, projects * 0.1)
        
        # Experience (15%)
        experience = len(data.get('experience', []))
        score += min(0.15, experience * 0.075)
        
        # Education (5%)
        education = len(data.get('education', []))
        score += min(0.05, education * 0.025)
        
        return round(min(score, 1.0), 3)
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self._warnings.copy()