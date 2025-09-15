from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PipelineState(BaseModel):
    #Pipeline Metadata
    pipeline_id: str = Field(default="pipeline_001", description="Unique ID for the pipeline run")
    current_step: str = Field(default="init", description="The last agent that updated the state")
    status: str = Field(default="in_progress", description="Pipeline execution status")
    #Lead Info
    lead: Dict[str, Any] = Field(default_factory=dict, description="Raw lead data from research")
    qualified_lead: Dict[str, Any] = Field(default_factory=dict, description="Qualified lead details")
    outreach_email: Optional[str] = Field(default=None, description="Generated Personalized email")
    followup_plan: Optional[str] = Field(default=None, description="Planned followup action")
    #Error Tracking
    errors: Dict[str, str] = Field(default_factory=dict, description="Agent specific error logs")
    
    def update_step(self, agent_name: str):
        self.current_step = agent_name
        
    def add_error(self, agent_name: str, error_msg: str):
        self.errors[agent_name] = error_msg
        self.status = "error"
    