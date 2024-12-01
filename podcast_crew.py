# ===============================
# File: podcast_crew.py
# ===============================
from crewai import Agent, Crew, Task
from tools import audio_transcriber
from config import OPENAI_API_KEY, PPLX_API_KEY
import yaml
import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatPerplexity

class PodcastCrew:
    """Podcast summarizer Crew"""

    def __init__(self):
        # Load configurations
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        if self.agents_config is None or self.tasks_config is None:
            raise ValueError("Failed to load configurations.")

        # Load audio transcriber tool
        self.audio_tool = [audio_transcriber]

        # Configure model from OpenAI
        self.openai_api_key = OPENAI_API_KEY
        self.gpt_llm = ChatOpenAI(
            temperature=0.2,
            openai_api_key=self.openai_api_key,
            model="openai/gpt-4-1106-preview"
        )

        # Configure Perplexity Llama-3.1-Sonar using Perplexity's API
        self.perplexity_api_key = PPLX_API_KEY
        self.pplx_llm = ChatPerplexity(
            api_key=self.perplexity_api_key,
            model="perplexity/llama-3.1-sonar-huge-128k-online"
        )

        # Initialize agents and tasks in the correct order
        self.agents = self._create_agents()
        self.tasks = []  # Initialize empty task list
        self._create_tasks()  # Create tasks with proper dependencies

    def _create_agents(self):
        return {
            'transcriber': Agent(
                role=self.agents_config['transcriber']['role'],
                goal=self.agents_config['transcriber']['goal'],
                backstory=self.agents_config['transcriber']['backstory'],
                tools=self.audio_tool,
                verbose=True,
                llm=self.gpt_llm
            ),
            'summarizer': Agent(
                role=self.agents_config['summarizer']['role'],
                goal=self.agents_config['summarizer']['goal'],
                backstory=self.agents_config['summarizer']['backstory'],
                tools=[],
                verbose=True,
                llm=self.gpt_llm
            ),
            'action_point_specialist': Agent(
                role=self.agents_config['action_point_specialist']['role'],
                goal=self.agents_config['action_point_specialist']['goal'],
                backstory=self.agents_config['action_point_specialist']['backstory'],
                tools=[],
                verbose=True,
                llm=self.gpt_llm
            ),
            'content_auditor': Agent(
                role=self.agents_config['content_auditor']['role'],
                goal=self.agents_config['content_auditor']['goal'],
                backstory=self.agents_config['content_auditor']['backstory'],
                tools=[],
                verbose=True,
                llm=self.gpt_llm
            ),
            'claims_analyst': Agent(
                role=self.agents_config['claims_analyst']['role'],
                goal=self.agents_config['claims_analyst']['goal'],
                backstory=self.agents_config['claims_analyst']['backstory'],
                tools=[],
                verbose=True,
                llm=self.gpt_llm
            ),
            'fact_checker': Agent(
                role=self.agents_config['fact_checker']['role'],
                goal=self.agents_config['fact_checker']['goal'],
                backstory=self.agents_config['fact_checker']['backstory'],
                tools=[],
                verbose=True,
                llm=self.pplx_llm
            )
        }

    def _create_tasks(self):
        """Create all tasks for the crew with proper dependencies"""
        
        # Transcription task (no dependencies)
        transcription_task = Task(
            description=self.tasks_config['transcription_task']['description'],
            expected_output="A complete text transcription of the YouTube video's audio content.",
            agent=self.agents['transcriber']
        )
        self.tasks.append(transcription_task)

        # Summary task (depends on transcription)
        summary_task = Task(
            description=self.tasks_config['summary_task']['description'],
            expected_output="A concise summary of the key points discussed in the podcast.",
            agent=self.agents['summarizer'],
            context=[transcription_task]
        )
        self.tasks.append(summary_task)

        # Actionable insights task (depends on summary)
        insights_task = Task(
            description=self.tasks_config['actionable_insights_task']['description'],
            expected_output="A list of actionable insights and takeaways from the podcast content.",
            agent=self.agents['action_point_specialist'],
            context=[summary_task]
        )
        self.tasks.append(insights_task)

        # Claims identification task (depends on transcription and summary)
        claims_task = Task(
            description=self.tasks_config['claims_identification_task']['description'],
            expected_output="A list of significant claims made during the podcast that require fact-checking.",
            agent=self.agents['claims_analyst'],
            context=[transcription_task, summary_task]
        )
        self.tasks.append(claims_task)

        # Fact checking task (depends on claims identification)
        fact_check_task = Task(
            description=self.tasks_config['fact_checking_task']['description'],
            expected_output="A detailed analysis of the accuracy of identified claims with supporting evidence.",
            agent=self.agents['fact_checker'],
            context=[claims_task]
        )
        self.tasks.append(fact_check_task)

        # Quality audit task (depends on all previous tasks)
        audit_task = Task(
            description=self.tasks_config['quality_audit_task']['description'],
            expected_output="A comprehensive quality assessment of all previous analyses and a final report.",
            agent=self.agents['content_auditor'],
            context=[transcription_task, summary_task, insights_task, claims_task, fact_check_task]
        )
        self.tasks.append(audit_task)

    def kickoff(self, inputs):
        """Start the crew's work"""
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            verbose=True
        )
        
        result = crew.kickoff(inputs=inputs)
        return result