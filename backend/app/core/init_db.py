from sqlalchemy.orm import Session
from app.core.database import Base, engine, ensure_db_schema_sync
from app.models import Role, Skill
from app.core.logging import logger

INITIAL_ROLES = [
    {"name": "Full Stack Developer", "normalized_name": "full stack developer"},
    {"name": "Frontend Developer", "normalized_name": "frontend developer"},
    {"name": "Backend Developer", "normalized_name": "backend developer"},
    {"name": "Software Engineer", "normalized_name": "software engineer"},
    {"name": "DevOps Engineer", "normalized_name": "devops engineer"},
    {"name": "Data Engineer", "normalized_name": "data engineer"},
    {"name": "Python Developer", "normalized_name": "python developer"},
    {"name": "React Developer", "normalized_name": "react developer"},
    {"name": "Node.js Developer", "normalized_name": "node.js developer"},
]

INITIAL_SKILLS = [
    # Frontend
    {"name": "React", "normalized_name": "react", "category": "Frontend", "aliases": ["reactjs", "react.js", "react js"]},
    {"name": "Next.js", "normalized_name": "next.js", "category": "Frontend", "aliases": ["nextjs", "next.js", "next js", "next"]},
    {"name": "TypeScript", "normalized_name": "typescript", "category": "Language", "aliases": ["ts", "type script"]},
    {"name": "JavaScript", "normalized_name": "javascript", "category": "Language", "aliases": ["js", "ecmascript", "javascript es6"]},
    {"name": "Tailwind CSS", "normalized_name": "tailwind css", "category": "Frontend", "aliases": ["tailwind", "tailwindcss", "tailwind-css"]},
    {"name": "HTML/CSS", "normalized_name": "html/css", "category": "Frontend", "aliases": ["html", "css", "html5", "css3"]},
    {"name": "Vue.js", "normalized_name": "vue.js", "category": "Frontend", "aliases": ["vue", "vuejs", "vue.js"]},
    {"name": "Angular", "normalized_name": "angular", "category": "Frontend", "aliases": ["angularjs", "angular 2+"]},

    # Backend & Languages
    {"name": "Python", "normalized_name": "python", "category": "Language", "aliases": ["python3", "py"]},
    {"name": "Node.js", "normalized_name": "node.js", "category": "Backend", "aliases": ["node", "nodejs", "node js"]},
    {"name": "FastAPI", "normalized_name": "fastapi", "category": "Backend", "aliases": ["fast api", "fastapi framework"]},
    {"name": "Express.js", "normalized_name": "express.js", "category": "Backend", "aliases": ["express", "expressjs", "express js"]},
    {"name": "Django", "normalized_name": "django", "category": "Backend", "aliases": ["django rest framework", "drf"]},
    {"name": "Java", "normalized_name": "java", "category": "Language", "aliases": ["java core", "spring", "spring boot"]},
    {"name": "Go", "normalized_name": "go", "category": "Language", "aliases": ["golang"]},
    {"name": "C#", "normalized_name": "c#", "category": "Language", "aliases": [".net", "asp.net", "csharp"]},
    {"name": "REST API", "normalized_name": "rest api", "category": "Backend", "aliases": ["rest", "restful", "restful api", "rest apis"]},
    {"name": "GraphQL", "normalized_name": "graphql", "category": "Backend", "aliases": ["graph ql", "apollo"]},

    # Databases
    {"name": "PostgreSQL", "normalized_name": "postgresql", "category": "Database", "aliases": ["postgres", "postgressql", "psql"]},
    {"name": "MongoDB", "normalized_name": "mongodb", "category": "Database", "aliases": ["mongo", "nosql"]},
    {"name": "Redis", "normalized_name": "redis", "category": "Database", "aliases": ["redis cache"]},
    {"name": "MySQL", "normalized_name": "mysql", "category": "Database", "aliases": ["my-sql", "mariadb"]},
    {"name": "SQL", "normalized_name": "sql", "category": "Database", "aliases": ["relational database", "rdbms"]},

    # Cloud & DevOps
    {"name": "AWS", "normalized_name": "aws", "category": "Cloud/DevOps", "aliases": ["amazon web services", "ec2", "s3", "lambda", "aws cloud"]},
    {"name": "Docker", "normalized_name": "docker", "category": "Cloud/DevOps", "aliases": ["docker containers", "containerization"]},
    {"name": "Kubernetes", "normalized_name": "kubernetes", "category": "Cloud/DevOps", "aliases": ["k8s", "k8"]},
    {"name": "CI/CD", "normalized_name": "ci/cd", "category": "Cloud/DevOps", "aliases": ["github actions", "jenkins", "gitlab ci", "continuous integration"]},
    {"name": "Git", "normalized_name": "git", "category": "Tools", "aliases": ["github", "gitlab", "version control"]},
    {"name": "Linux", "normalized_name": "linux", "category": "Tools", "aliases": ["ubuntu", "bash", "shell scripting"]},
    {"name": "Testing", "normalized_name": "testing", "category": "Tools", "aliases": ["unit testing", "jest", "pytest", "cypress", "playwright", "integration testing"]},
]


def init_db(db: Session):
    """Create all tables and seed standard roles & canonical skills."""
    Base.metadata.create_all(bind=engine)
    ensure_db_schema_sync()

    # Seed roles
    for role_data in INITIAL_ROLES:
        existing = db.query(Role).filter(Role.normalized_name == role_data["normalized_name"]).first()
        if not existing:
            db.add(Role(name=role_data["name"], normalized_name=role_data["normalized_name"]))

    # Seed skills
    for skill_data in INITIAL_SKILLS:
        existing = db.query(Skill).filter(Skill.normalized_name == skill_data["normalized_name"]).first()
        if not existing:
            db.add(Skill(
                name=skill_data["name"],
                normalized_name=skill_data["normalized_name"],
                category=skill_data["category"],
                aliases=skill_data["aliases"]
            ))

    db.commit()
    logger.info("Database schema verified and canonical dictionary seeded successfully.")
