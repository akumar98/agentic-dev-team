import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

def build_crew_result(idea: str) -> str:
    llm = LLM(
        model="claude-haiku-4-5",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    requirements_agent = Agent(
        role="Requirements Agent",
        goal="Turn a product idea into clear user stories and acceptance criteria.",
        backstory="You are a senior product analyst for greenfield software projects.",
        llm=llm,
    )

    architecture_agent = Agent(
        role="Architecture Agent",
        goal="Design the technical architecture, data model, APIs, and stack.",
        backstory="You are a principal software architect.",
        llm=llm,
    )

    developer_agent = Agent(
        role="Developer Agent",
        goal="Create implementation tasks and code structure for the app.",
        backstory="You are a senior full-stack engineer.",
        llm=llm,
    )

    testing_agent = Agent(
        role="Testing Agent",
        goal="Create unit, integration, and end-to-end test plans.",
        backstory="You are a QA automation engineer.",
        llm=llm,
    )

    task1 = Task(
        description=f"Create a PRD for this app: {idea}",
        agent=requirements_agent,
        expected_output="A detailed PRD with features, user stories, and acceptance criteria.",
    )

    task2 = Task(
        description="Create the architecture, data model, API design, and recommended stack.",
        agent=architecture_agent,
        expected_output="Architecture document with database schema and API routes.",
    )

    task3 = Task(
        description="Create implementation tasks for frontend, backend, database, and deployment.",
        agent=developer_agent,
        expected_output="A detailed engineering task breakdown.",
    )

    task4 = Task(
        description="Create a test strategy for the application.",
        agent=testing_agent,
        expected_output="Unit, integration, security, and E2E test plan.",
    )

    crew = Crew(
        agents=[requirements_agent, architecture_agent, developer_agent, testing_agent],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
    )

    return str(crew.kickoff())

if __name__ == "__main__":
    default_idea = (
        "Build an investor CRM with login, investor profiles, notes, tasks, "
        "dashboard metrics, and search/filtering."
    )
    print(build_crew_result(default_idea))