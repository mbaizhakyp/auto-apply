import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from src.intelligence.models import UserProfile, TailoredContent

class PDFGenerator:
    def __init__(self, template_dir: str = "src/generator/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_resume(self, user_profile: UserProfile, tailored_content: TailoredContent, job_title: str, output_path: str):
        template = self.env.get_template("resume.html")
        
        # Combine base profile with tailored content
        # For MVP we just pass them as context variables
        html_content = template.render(
            user=user_profile,
            bullet_points=tailored_content.resume_bullet_points,
            skills=user_profile.skills, # Could be tailored too
            job_title=job_title
        )
        
        HTML(string=html_content).write_pdf(output_path)
        return output_path
