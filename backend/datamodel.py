from datetime import datetime
from enum import Enum
from types import NoneType
from typing import Any, Callable, Dict, List, Literal, Optional, Union
from pydantic import validator, root_validator

import json
from openai.types.chat.chat_completion_named_tool_choice_param import Function
from sqlalchemy.types import TypeDecorator, String
from pydantic_core.core_schema import int_schema
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy import ForeignKey, Integer, orm
from sqlalchemy.sql.expression import False_
from sqlmodel import (
    JSON,
    Column,
    DateTime,
    Field,
    Relationship,
    SQLModel,
    func,
)
from sqlmodel import (
    Enum as SqlEnum,
)

SQLModel.model_config["protected_namespaces"] = ()
SQLModel.model_config["arbitrary_types_allowed"] = True

# pylint: disable=protected-access


class Message(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    role: str
    content: str
    session_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("session.id", ondelete="CASCADE")),
    )
    connection_id: Optional[str] = None
    meta: Optional[Dict] = Field(default={}, sa_column=Column(JSON))


class Session(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    name: Optional[str] = None
    description: Optional[str] = None


class AgentSkillLink(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    agent_id: int = Field(default=None, primary_key=True, foreign_key="agent.id")
    skill_id: int = Field(default=None, primary_key=True, foreign_key="skill.id")


class AgentModelLink(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    agent_id: int = Field(default=None, primary_key=True, foreign_key="agent.id")
    model_id: int = Field(default=None, primary_key=True, foreign_key="model.id")


# Skill is hard function, or imperative functions, implemented in some programming language,
# In this case, python.
class Skill(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    name: str
    content: str
    description: Optional[str] = None
    secrets: Optional[Dict] = Field(default={}, sa_column=Column(JSON))
    libraries: Optional[Dict] = Field(default={}, sa_column=Column(JSON))
    agents: List["Agent"] = Relationship(
        back_populates="skills", link_model=AgentSkillLink
    )


class LLMConfig(SQLModel, table=False):
    """Data model for LLM Config for AutoGen"""

    config_list: List[Any] = Field(default_factory=list)
    temperature: float = 0
    cache_seed: Optional[Union[int, None]] = None
    timeout: Optional[int] = None
    max_tokens: Optional[int] = 1000
    extra_body: Optional[dict] = None


class ModelTypes(str, Enum):
    openai = "open_ai"
    google = "google"
    azure = "azure"


# This is used to specify how LLM is used.
class Model(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    api_type: ModelTypes = Field(
        default=ModelTypes.openai, sa_column=Column(SqlEnum(ModelTypes))
    )
    api_version: Optional[str] = None
    description: Optional[str] = None
    agents: List["Agent"] = Relationship(
        back_populates="models", link_model=AgentModelLink
    )

    def getLabel(self) -> str:
        # @Hui, change the implementation here. For now it returns a dummy.
        return "groq/llama-3.1-70b-versatile"


class CodeExecutionConfigTypes(str, Enum):
    local = "local"
    docker = "docker"
    none = "none"


class AgentConfig(SQLModel, table=False):
    name: Optional[str] = None
    human_input_mode: str = "NEVER"
    max_consecutive_auto_reply: int = 10
    system_message: Optional[str] = None
    is_termination_msg: Optional[Union[bool, str, Callable]] = None
    code_execution_config: CodeExecutionConfigTypes = Field(
        default=CodeExecutionConfigTypes.local,
        sa_column=Column(SqlEnum(CodeExecutionConfigTypes)),
    )
    default_auto_reply: Optional[str] = ""
    description: Optional[str] = None
    llm_config: Optional[Union[LLMConfig, bool]] = Field(
        default=False, sa_column=Column(JSON)
    )

    admin_name: Optional[str] = "Admin"
    messages: Optional[List[Dict]] = Field(default_factory=list)
    max_round: Optional[int] = 100
    speaker_selection_method: Optional[str] = "auto"
    allow_repeat_speaker: Optional[Union[bool, List["AgentConfig"]]] = True


class AgentType(str, Enum):
    assistant = "assistant"
    userproxy = "userproxy"
    groupchat = "groupchat"


class WorkflowAgentType(str, Enum):
    sender = "sender"
    receiver = "receiver"
    planner = "planner"


class WorkflowAgentLink(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    workflow_id: int = Field(default=None, primary_key=True, foreign_key="workflow.id")
    agent_id: int = Field(default=None, primary_key=True, foreign_key="agent.id")
    agent_type: WorkflowAgentType = Field(
        default=WorkflowAgentType.sender,
        sa_column=Column(SqlEnum(WorkflowAgentType), primary_key=True),
    )


class AgentLink(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    parent_id: Optional[int] = Field(
        default=None, foreign_key="agent.id", primary_key=True
    )
    agent_id: Optional[int] = Field(
        default=None, foreign_key="agent.id", primary_key=True
    )


class SingleIntType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        data = None
        if value is not None:
            data = value.get("id", None)

        return data

    def process_result_value(self, value, dialect):
        return value


class ListType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return ""

    def process_result_value(self, value, dialect):
        return []


class ArrayType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        data = []
        if value is not None:
            data = [o.get("id") if o is not None else None for o in value]

        return json.dumps(data)

    def process_result_value(self, value, dialect):
        data = []

        if value is not None:
            try:
                data = json.loads(value)
            except:
                pass
        return data


# Agent is simply a LLM based module.
class Agent(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    type: AgentType = Field(
        default=AgentType.assistant, sa_column=Column(SqlEnum(AgentType))
    )
    config: AgentConfig = Field(default_factory=AgentConfig, sa_column=Column(JSON))
    skills: List[Skill] = Relationship(
        back_populates="agents", link_model=AgentSkillLink
    )
    models: List[Model] = Relationship(
        back_populates="agents", link_model=AgentModelLink
    )
    workflows: List["Workflow"] = Relationship(
        link_model=WorkflowAgentLink, back_populates="agents"
    )
    parents: List["Agent"] = Relationship(
        back_populates="agents",
        link_model=AgentLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Agent.id==AgentLink.agent_id",
            secondaryjoin="Agent.id==AgentLink.parent_id",
        ),
    )
    agents: List["Agent"] = Relationship(
        back_populates="parents",
        link_model=AgentLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Agent.id==AgentLink.parent_id",
            secondaryjoin="Agent.id==AgentLink.agent_id",
        ),
    )
    schema_base: bool = True
    schema_id: Optional[int] = None
    code_skill_id: Optional[int] = None
    functions: Optional[List[Skill]] = Field(default=None, sa_column=Column(ListType))


class WorkFlowType(str, Enum):
    twoagents = "twoagents"
    groupchat = "groupchat"


class WorkFlowSummaryMethod(str, Enum):
    last = "last"
    none = "none"
    llm = "llm"


class Workflow(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )  # pylint: disable=not-callable
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )  # pylint: disable=not-callable
    user_id: Optional[str] = None
    name: str
    description: str
    agents: List[Agent] = Relationship(
        back_populates="workflows", link_model=WorkflowAgentLink
    )
    type: WorkFlowType = Field(
        default=WorkFlowType.twoagents, sa_column=Column(SqlEnum(WorkFlowType))
    )
    summary_method: Optional[WorkFlowSummaryMethod] = Field(
        default=WorkFlowSummaryMethod.last,
        sa_column=Column(SqlEnum(WorkFlowSummaryMethod)),
    )


class Response(SQLModel):
    message: str
    status: bool
    data: Optional[Any] = None


class SocketMessage(SQLModel, table=False):
    connection_id: str
    data: Dict[str, Any]
    type: str


class SchemaFieldTrueType(str, Enum):
    any = "Any"
    int = "int"
    float = "float"
    boolean = "bool"
    string = "str"


class SchemaFieldMode(str, Enum):
    any = "any"
    input = "input"
    output = "output"


class MetricType(str, Enum):
    agent = "agent"
    skill = "skill"


class SchemaField(SQLModel, table=False):
    name: str
    description: str
    true_type: SchemaFieldTrueType = Field(
        default=SchemaFieldTrueType.any, sa_column=Column(SqlEnum(SchemaFieldTrueType))
    )
    mode: SchemaFieldMode = Field(
        default=SchemaFieldMode.any, sa_column=Column(SqlEnum(SchemaFieldMode))
    )
    prefix: str

    @validator("true_type", pre=True, always=True)
    def validate_true_type(cls, v):
        if isinstance(v, SchemaFieldTrueType):
            return v.value
        if v == "string":
            return SchemaFieldTrueType.string
        if v == "bool":
            return SchemaFieldTrueType.boolean
        return v

    @validator("mode", pre=True, always=True)
    def validate_mode(cls, v):
        if isinstance(v, SchemaFieldMode):
            return v.value
        return v


class Schema(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )
    isHide: bool = False
    user_id: Optional[str] = None
    name: str
    description: str
    fields: List[SchemaField] = Field(
        default_factory=List[SchemaField], sa_column=Column(JSON)
    )


# @Hui, can we change this to collection instead?
class Collections(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )
    user_id: Optional[str] = None
    name: str
    description: str
    schema_id: Optional[int] = None

    external: bool | None = None
    url: str | None = None
    fieldMapping: Dict | None = Field(default={}, sa_column=Column(JSON))


class CollectionRow(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )
    collection_id: int
    data: Optional[Dict] = Field(default={}, sa_column=Column(JSON))


class PromptStrategyEnum(str, Enum):
    predict = "Predict"
    chain_of_thought = "ChainOfThought"
    re_act = "ReAct"


class OptimizerEnum(str, Enum):
    bootstrap_few_shot = "BootstrapFewShot"
    labeled_few_shot = "LabeledFewShot"
    bootstrap_few_shot_with_random_search = "BootstrapFewShotWithRandomSearch"
    bootstrap_few_shot_with_optuna_knnfewshot = "BootstrapFewShotWithOptuna, KNNFewShot"


class SignatureCompileRequest(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )

    agent_id: int
    models: List[Model] = Field(default=[], sa_column=Column(ArrayType))
    training_sets: List[Collections] = Field(default=[], sa_column=Column(ArrayType))
    development_sets: List[Collections] = Field(default=[], sa_column=Column(ArrayType))

    prompt_strategy: PromptStrategyEnum = Field(
        default=PromptStrategyEnum.predict,
        sa_column=Column(SqlEnum(PromptStrategyEnum)),
    )
    optimizer: Optional[OptimizerEnum] = Field(
        default=None, sa_column=Column(SqlEnum(OptimizerEnum))
    )

    metric_id: int
    metric_type: MetricType = Field(sa_column=Column(SqlEnum(MetricType)))

    name: str = ""
    description: str = ""

    # These API will be used by code gen so that it does not need to know
    # how this information is stored.

    def setAgent(self, agent: Agent):
        self.__table_args__["agent"] = agent

    def getAgent(self) -> Agent:
        return self.__table_args__["agent"]

    def getWorkerModel(self) -> Model:
        pass

    def setSchema(self, schema: Schema):
        self.__table_args__["schema"] = schema

    def getSchema(self) -> Schema:
        return self.__table_args__["schema"]


class Implementation(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: Optional[int] = None
    name: str
    user_id: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    generated_prompt: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )


class Evaluation(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}
    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: Optional[int] = None
    implementation_id: Optional[int] = None

    collection: Optional[Collections] = Field(
        default=None, sa_column=Column(SingleIntType)
    )

    metric_id: int
    metric_type: MetricType = Field(sa_column=Column(SqlEnum(MetricType)))

    result: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )


class ImplementationTestRequest(SQLModel, table=False):
    implementation_id: int
    inputs: Dict = Field(default={}, sa_column=Column(JSON))


class ImplementationTestResponse(SQLModel, table=False):
    result: Dict = Field(default={}, sa_column=Column(JSON))
