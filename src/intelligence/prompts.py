from langchain_core.prompts import ChatPromptTemplate

FIT_ANALYSIS_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert Career Coach and Technical Recruiter.
    
    Evaluate the following Job Description against the Candidate Profile.
    
    CANDIDATE PROFILE:
    {user_profile}
    
    JOB DESCRIPTION:
    {job_description}
    
    Your goal is to Determine a Fit Score (0-100) and decide if we should APPLY or REJECT.
    - Score > 80: Strong Match (Apply)
    - Score > 60: Potential Match (Apply if few applicants)
    - Score < 60: Poor Match (Reject)
    
    Also extract the specific technical requirements and sponsorship availability.
    
    Return the output in the specified JSON format.
    """
)

TAILORING_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert Resume Writer.
    
    Draft a custom Cover Letter and tailored Resume Bullet Points for the following application.
    
    CANDIDATE BASE RESUME:
    {resume_text}
    
    JOB REQUIREMENTS (Extracted):
    {job_requirements}
    
    JOB DESCRIPTION:
    {job_description}
    
    The Cover Letter should be professional, concise (max 200 words), and efficient.
    The Bullet Points should highlight the candidate's experience specifically relevant to the job requirements.
    
    Return the output in the specified JSON format.
    """
)
