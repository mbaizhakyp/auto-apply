from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from src.intelligence.engine import IntelligenceEngine
from src.intelligence.models import FitAnalysis, TailoredContent, UserProfile
from src.database.models import Job

class AgentState(TypedDict):
    job: Job
    user_profile: UserProfile
    fit_analysis: Annotated[FitAnalysis, "Fit Analysis Result"]
    tailored_content: Annotated[TailoredContent, "Tailored Content"]
    decision: str

class ApplicationWorkflow:
    def __init__(self, engine: IntelligenceEngine):
        self.engine = engine
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("analyze_fit", self.analyze_fit_node)
        workflow.add_node("tailor_content", self.tailor_content_node)
        workflow.add_node("archive_job", self.archive_job_node)

        workflow.set_entry_point("analyze_fit")

        workflow.add_conditional_edges(
            "analyze_fit",
            self.should_apply,
            {
                "apply": "tailor_content",
                "reject": "archive_job"
            }
        )

        workflow.add_edge("tailor_content", END)
        workflow.add_edge("archive_job", END)

        return workflow.compile()

    async def analyze_fit_node(self, state: AgentState):
        job = state["job"]
        # Allow text or html, handle missing text logic elsewhere or assume populated
        description = job.description_text or job.description_html or ""
        
        analysis = await self.engine.analyze_fit(description, state["user_profile"])
        
        return {
            "fit_analysis": analysis,
            "decision": "APPLY" if analysis.score > 60 else "REJECT" # Simple threshold
        }

    async def tailor_content_node(self, state: AgentState):
        job = state["job"]
        analysis = state["fit_analysis"]
        description = job.description_text or ""
        
        content = await self.engine.tailor_application(
            description, 
            analysis.matching_skills, # Using matching skills as proxy for requirements context
            state["user_profile"]
        )
        
        return {"tailored_content": content}

    async def archive_job_node(self, state: AgentState):
        # In a real app we would update DB status here or return a flag
        return {"decision": "REJECTED"}

    def should_apply(self, state: AgentState):
        return "apply" if state["decision"] == "APPLY" else "reject"
