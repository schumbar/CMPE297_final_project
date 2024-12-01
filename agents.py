# ===============================
# File: agents.py
# ===============================
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import AIMessage, HumanMessage
from langchain.tools import Tool
from typing import List, Dict
from utils import get_youtube_transcription
import yaml

class PodcastAnalyzer:
    def __init__(self, openai_api_key: str, perplexity_api_key: str):
        # Load configurations
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        if not self.agents_config or not self.tasks_config:
            raise ValueError("Failed to load YAML configurations")

        # Map agent types to task names
        self.task_map = {
            "transcriber": "transcription_task",
            "summarizer": "summary_task",
            "action_point_specialist": "actionable_insights_task",
            "claims_analyst": "claims_identification_task",
            "fact_checker": "fact_checking_task",
            "content_auditor": "quality_audit_task"
        }

        # Configure models
        self.gpt_llm = ChatOpenAI(
            temperature=0.2,
            model="gpt-4",
            openai_api_key=openai_api_key
        )
        
        self.pplx_llm = ChatPerplexity(
            api_key=perplexity_api_key,
            model="llama-3.1-sonar-huge-128k-online"
        )

    def _create_agent_prompt(self, agent_type: str, input_text: str) -> str:
        """Create a prompt from agent configuration"""
        agent_config = self.agents_config[agent_type]
        task_name = self.task_map[agent_type]
        task_config = self.tasks_config[task_name]
        
        # Replace any placeholders in the task description
        task_description = task_config['description']
        if '{youtube_url}' in task_description:
            task_description = task_description.replace('{youtube_url}', input_text)

        return f"""Role: {agent_config['role']}

Goal: {agent_config['goal']}

Background: {agent_config['backstory']}

Task: {task_description}

Expected Output: {task_config['expected_output']}

Input: {input_text}"""

    def _process_with_agent(self, text: str, agent_type: str, model=None) -> str:
        """Process text using specified agent configuration"""
        prompt = self._create_agent_prompt(agent_type, text)
        llm = model or self.gpt_llm
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
        
        response = llm.invoke(messages)
        return response.content

    def analyze_podcast(self, youtube_url: str) -> Dict:
        """Main function to analyze podcast content"""
        try:
            # 1. Transcription
            transcript = get_youtube_transcription(youtube_url)
            if not transcript or transcript.startswith("Error"):
                raise Exception(f"Transcription failed: {transcript}")

            # 2. Summary using the summarizer agent
            summary = self._process_with_agent(transcript, "summarizer")
            
            # 3. Action Points using the action_point_specialist agent
            actions = self._process_with_agent(transcript, "action_point_specialist")
            
            # 4. Claims Analysis using the claims_analyst agent
            claims = self._process_with_agent(transcript, "claims_analyst")
            
            # 5. Fact Checking using the fact_checker agent (with Perplexity)
            facts = self._process_with_agent(claims, "fact_checker", self.pplx_llm)
            
            # 6. Final Audit using the content_auditor agent
            audit_input = f"""
Summary: {summary}

Action Points: {actions}

Claims Analysis: {claims}

Fact Check Results: {facts}
"""
            final_output = self._process_with_agent(audit_input, "content_auditor")
            
            return {
                "raw_transcript": transcript,
                "summary": summary,
                "action_points": actions,
                "claims": claims,
                "fact_check": facts,
                "final_analysis": final_output
            }
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")