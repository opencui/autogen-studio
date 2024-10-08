import React from "react";
import { CollapseBox, ControlRowView } from "../../../atoms";
import { checkAndSanitizeInput, fetchJSON, getServerUrl } from "../../../utils";
import {
  Button,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Slider,
  Switch,
  Table,
  Tabs,
  message,
  theme,
} from "antd";
import { LeftOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import {
  BugAntIcon,
  CpuChipIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import { appContext } from "../../../../hooks/provider";
import {
  AgentSelector,
  AgentTypeSelector,
  ModelSelector,
  SkillSelector,
} from "./selectors";
import { IAgent, ICollection, IEvaluation, IImplementation, ILLMConfig, IModelConfig, ISchema, ISignatureCompileRequest, ISkill } from "../../../types";
import TextArea from "antd/es/input/TextArea";
import { cloneDeep } from "lodash";
import { Agent } from "http";

const { useToken } = theme;

export const AgentConfigView = ({
  agent,
  setAgent,
  schemas,
  skills,
  close,
}: {
  agent: IAgent;
  setAgent: (agent: IAgent) => void;
  schemas: ISchema[];
  skills: ISkill[];
  close: () => void;
}) => {
  const nameValidation = checkAndSanitizeInput(agent?.config?.name);
  const [error, setError] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const { user } = React.useContext(appContext);
  const serverUrl = getServerUrl();
  const createAgentUrl = `${serverUrl}/agents`;

  const [controlChanged, setControlChanged] = React.useState<boolean>(false);

  const onControlChange = (value: any, key: string) => {
    // if (key === "llm_config") {
    //   if (value.config_list.length === 0) {
    //     value = false;
    //   }
    // }
    const updatedAgent = {
      ...agent,
      config: { ...agent.config, [key]: value },
    };

    setAgent(updatedAgent);
    setControlChanged(true);
  };

  const onAgentChange = (value: any, key: string) => {

    const updatedAgent = {
      ...agent,
      [key]: value,
    };

    setAgent(updatedAgent);
    setControlChanged(true);
  };

  const llm_config: ILLMConfig = agent?.config?.llm_config || {
    config_list: [],
    temperature: 0.1,
    max_tokens: 1000,
  };

  const saveAgent = (agent: IAgent) => {
    setError(null);
    setLoading(true);

    agent.user_id = user?.email;
    const payLoad = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(agent),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);

        const newAgent = data.data;
        setAgent(newAgent);
      } else {
        message.error(data.message);
      }
      setLoading(false);
      // setNewAgent(sampleAgent);
    };
    const onError = (err: any) => {
      setError(err);
      message.error(err.message);
      setLoading(false);
    };
    const onFinal = () => {
      setLoading(false);
      setControlChanged(false);
    };

    fetchJSON(createAgentUrl, payLoad, onSuccess, onError, onFinal);
  };

  const hasChanged =
    (!controlChanged || !nameValidation.status) && agent?.id !== undefined;

  return (
    <div className="text-primary">
      <Form>
        <div
        // className={`grid  gap-3 ${agent.type === "groupchat" ? "grid-cols-2" : "grid-cols-1"
        //   }`}
        >
          <div className="">
            <ControlRowView
              title="Name"
              className=""
              description="Name of the module"
              value=""
              control={
                <>
                  <Input
                    className="mt-2"
                    placeholder="Module Name"
                    value={agent?.config?.name}
                    onChange={(e) => {
                      onControlChange(e.target.value, "name");
                    }}
                  />
                  {!nameValidation.status && (
                    <div className="text-xs text-red-500 mt-2">
                      {nameValidation.message}
                    </div>
                  )}
                </>
              }
            />

            <ControlRowView
              title="Description"
              className="mt-4"
              description=""
              value={""}
              control={
                <Input
                  className="mt-2"
                  placeholder="Module Description"
                  value={agent.config.description || ""}
                  onChange={(e) => {
                    onControlChange(e.target.value, "description");
                  }}
                />
              }
            />
            <ControlRowView
              title="Schema based"
              className="mt-4"
              description=""
              value={""}
              titleExtra={
                <Switch value={agent.schema_base} onChange={(checked) => {
                  onAgentChange(checked, "schema_base");
                }} />
              }
              control={""
              }
            />
            {agent.schema_base ? <ControlRowView
              title="Schema"
              className="mt-4"
              description=""
              value={""}
              extra={
                <Select
                  placeholder="Select schema"
                  value={agent.schema_id}
                  onChange={(value) => {
                    onAgentChange(value, "schema_id");
                  }}
                >
                  {
                    schemas.map((opt) =>
                      <Select.Option key={opt.id} value={opt.id}>
                        {
                          opt.name
                        }
                      </Select.Option>)
                  }
                </Select>
              }
              control={
                <Table
                  dataSource={agent.schema_id && schemas.filter((schema) => schema.id === agent.schema_id) || []}
                  columns={[{
                    title: "Name",
                    dataIndex: "name"
                  }, {
                    title: "Description",
                    dataIndex: "description"
                  }]}
                  pagination={false}
                  rowKey="id"
                />
              }
            />
              : <ControlRowView
                title="Class"
                className="mt-4"
                description=""
                value={""}
                extra={
                  <Select
                    placeholder="Select code function"
                    value={agent.code_skill_id}
                    onChange={(value) => {
                      onAgentChange(value, "code_skill_id");
                    }}
                  >
                    {
                      skills.map((opt) =>
                        <Select.Option key={opt.id} value={opt.id}>
                          {
                            opt.name
                          }
                        </Select.Option>)
                    }
                  </Select>
                }
                control={
                  <Table
                    dataSource={agent.code_skill_id && skills.filter((item) => item.id === agent.code_skill_id) || []}
                    columns={[{
                      title: "Name",
                      dataIndex: "name"
                    }, {
                      title: "Description",
                      dataIndex: "description"
                    }]}
                    pagination={false}
                    rowKey="id"
                  />
                }
              />
            }
            <ControlRowView
              title="Functions"
              className="mt-4"
              description=""
              value={""}
              extra={
                <Select
                  placeholder="Select function"
                  value={null}
                  onChange={(value) => {

                    const nextSkills = cloneDeep(agent.functions) || [];
                    const selected = skills.find((item) => item.id === value);

                    if (selected) {
                      nextSkills.push(selected);
                    }

                    onAgentChange(nextSkills, "functions");
                  }}
                >
                  {
                    skills.map((opt) =>
                      <Select.Option key={opt.id} value={opt.id} disabled={agent.functions?.findIndex((item) => item.id === opt.id) !== -1}>
                        {
                          opt.name
                        }
                      </Select.Option>)
                  }
                </Select>
              }
              control={
                <Table
                  pagination={false}
                  dataSource={agent.functions}
                  columns={[{
                    title: "Name",
                    dataIndex: "name"
                  }, {
                    title: "Description",
                    dataIndex: "description"
                  }, {
                    dataIndex: "",
                    width: 50,
                    render: (_, record, index) => {
                      return <div className="hidden-cell">
                        <DeleteOutlined
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();

                            const nextSkills = cloneDeep(agent.functions) || [];
                            nextSkills.splice(index, 1);
                            onAgentChange(nextSkills, "functions");
                          }}
                        />
                      </div>;
                    }
                  }]}
                  rowKey="id"
                />
              }
            />

            {/* <ControlRowView
              title="Max Consecutive Auto Reply"
              className="mt-4"
              description="Max consecutive auto reply messages before termination."
              // value={agent.config?.max_consecutive_auto_reply}
              value=""
              titleExtra={<InputNumber
                min={1}
                max={agent.type === "groupchat" ? 600 : 30}
                defaultValue={agent.config.max_consecutive_auto_reply}
                step={1}
                onChange={(value: any) => {
                  onControlChange(value, "max_consecutive_auto_reply");
                }}
              />}
              control={""
                // <Slider
                //   min={1}
                //   max={agent.type === "groupchat" ? 600 : 30}
                //   defaultValue={agent.config.max_consecutive_auto_reply}
                //   step={1}
                //   onChange={(value: any) => {
                //     onControlChange(value, "max_consecutive_auto_reply");
                //   }}
                // />
              }
            /> */}

            {/* <ControlRowView
              title="Human Input Mode"
              description="Defines when to request human input"
              // value={agent.config.human_input_mode}
              value=""
              titleExtra={
                <Select
                  className="mt-2 w-full"
                  defaultValue={agent.config.human_input_mode}
                  onChange={(value: any) => {
                    onControlChange(value, "human_input_mode");
                  }}
                  options={
                    [
                      { label: "NEVER", value: "NEVER" },
                      // { label: "TERMINATE", value: "TERMINATE" },
                      // { label: "ALWAYS", value: "ALWAYS" },
                    ] as any
                  }
                />
              }
              control={
                ""
              }
            /> */}

            <ControlRowView
              title="System Message"
              className="mt-4"
              description="Free text to control agent behavior"
              // value={agent.config.system_message}
              value=""
              control={
                <TextArea
                  className="mt-2 w-full"
                  value={agent.config.system_message}
                  rows={3}
                  onChange={(e) => {
                    onControlChange(e.target.value, "system_message");
                  }}
                />
              }
            />

            <div className="mt-4">
              {" "}
              <CollapseBox
                className="bg-secondary mt-4"
                open={false}
                title="Advanced Options"
              >
                <ControlRowView
                  title="Temperature"
                  className="mt-4"
                  description="Defines the randomness of the agent's response."
                  // value={llm_config.temperature}
                  value=""
                  titleExtra={
                    <InputNumber
                      min={0}
                      max={2}
                      step={0.1}
                      defaultValue={llm_config.temperature || 0.1}
                      onChange={(value: any) => {
                        const llm_config = {
                          ...agent.config.llm_config,
                          temperature: value,
                        };
                        onControlChange(llm_config, "llm_config");
                      }}
                    />
                  }
                  control={""
                    // <Slider
                    //   min={0}
                    //   max={2}
                    //   step={0.1}
                    //   defaultValue={llm_config.temperature || 0.1}
                    //   onChange={(value: any) => {
                    //     const llm_config = {
                    //       ...agent.config.llm_config,
                    //       temperature: value,
                    //     };
                    //     onControlChange(llm_config, "llm_config");
                    //   }}
                    // />
                  }
                />

                <ControlRowView
                  title="Agent Default Auto Reply"
                  className="mt-4"
                  description="Default auto reply when no code execution or llm-based reply is generated."
                  // value={agent.config.default_auto_reply || ""}
                  value=""
                  control={
                    <Input
                      className="mt-2"
                      placeholder="Agent Description"
                      value={agent.config.default_auto_reply || ""}
                      onChange={(e) => {
                        onControlChange(e.target.value, "default_auto_reply");
                      }}
                    />
                  }
                />

                <ControlRowView
                  title="Max Tokens"
                  description="Max tokens generated by LLM used in the agent's response."
                  // value={llm_config.max_tokens}
                  value=""
                  className="mt-4"
                  titleExtra={
                    <InputNumber
                      min={100}
                      max={50000}
                      defaultValue={llm_config.max_tokens || 1000}
                      onChange={(value: any) => {
                        const llm_config = {
                          ...agent.config.llm_config,
                          max_tokens: value,
                        };
                        onControlChange(llm_config, "llm_config");
                      }}
                    />
                  }
                  control=""
                />
                <ControlRowView
                  title="Code Execution Config"
                  className="mt-4"
                  description="Determines if and where code execution is done."
                  // value={agent.config.code_execution_config || "none"}
                  value=""
                  titleExtra={
                    <Select
                      className="mt-2"
                      defaultValue={
                        agent.config.code_execution_config || "none"
                      }
                      onChange={(value: any) => {
                        onControlChange(value, "code_execution_config");
                      }}
                      options={
                        [
                          { label: "None", value: "none" },
                          { label: "Local", value: "local" },
                          { label: "Docker", value: "docker" },
                        ] as any
                      }
                    />
                  }
                  control=""
                />
              </CollapseBox>
            </div>
          </div>
          {/* ====================== Group Chat Config ======================= */}
          {/* {agent.type === "groupchat" && (
            <div>
              <ControlRowView
                title="Speaker Selection Method"
                description="How the next speaker is selected"
                className=""
                // value={agent?.config?.speaker_selection_method || "auto"}
                value=""
                titleExtra={
                  <Select
                    className="mt-2 w-full"
                    defaultValue={
                      agent?.config?.speaker_selection_method || "auto"
                    }
                    onChange={(value: any) => {
                      if (agent?.config) {
                        onControlChange(value, "speaker_selection_method");
                      }
                    }}
                    options={
                      [
                        { label: "Auto", value: "auto" },
                        { label: "Round Robin", value: "round_robin" },
                        { label: "Random", value: "random" },
                      ] as any
                    }
                  />
                }
                control=""
              />

              <ControlRowView
                title="Admin Name"
                className="mt-4"
                description="Name of the admin of the group chat"
                // value={agent.config.admin_name || ""}
                value=""
                control={
                  <Input
                    className="mt-2"
                    placeholder="Agent Description"
                    value={agent.config.admin_name || ""}
                    onChange={(e) => {
                      onControlChange(e.target.value, "admin_name");
                    }}
                  />
                }
              />

              <ControlRowView
                title="Max Rounds"
                className="mt-4"
                description="Max rounds before termination."
                value={agent.config?.max_round || 10}
                control={
                  <Slider
                    min={10}
                    max={600}
                    defaultValue={agent.config.max_round}
                    step={1}
                    onChange={(value: any) => {
                      onControlChange(value, "max_round");
                    }}
                  />
                }
              />

              <ControlRowView
                title="Allow Repeat Speaker"
                className="mt-4"
                description="Allow the same speaker to speak multiple times in a row"
                value={agent.config?.allow_repeat_speaker || false}
                control={
                  <Select
                    className="mt-2 w-full"
                    defaultValue={agent.config.allow_repeat_speaker}
                    onChange={(value: any) => {
                      onControlChange(value, "allow_repeat_speaker");
                    }}
                    options={
                      [
                        { label: "True", value: true },
                        { label: "False", value: false },
                      ] as any
                    }
                  />
                }
              />
            </div>
          )} */}
        </div>
      </Form>

      <div className="w-full mt-4 text-right">
        {" "}
        {!hasChanged && (
          <Button
            type="primary"
            onClick={() => {
              saveAgent(agent);
              setAgent(agent);
            }}
            loading={loading}
          >
            {agent.id ? "Save" : "Create"}
          </Button>
        )}
        {/* <Button
          className="ml-2"
          key="close"
          type="default"
          onClick={() => {
            close();
          }}
        >
          Close
        </Button> */}
      </div>
    </div>
  );
};

export const AgentCompileView = ({ agentId, agent, models, collections, skills, agents }:
  {
    agentId: number;
    agent: IAgent;
    models: IModelConfig[];
    collections: ICollection[];
    skills: ISkill[];
    agents: IAgent[];
  }) => {

  const serverUrl = getServerUrl();

  const [loading, setLoading] = React.useState<boolean>(false);
  const [data, setData] = React.useState<ISignatureCompileRequest>({
    agent_id: agentId,
    models: [null, null],
    training_sets: [],
    development_sets: [],
    name: "",
    description: ""
  })

  const [saveName, setSaveName] = React.useState<string>("");
  const [saveDesc, setSaveDesc] = React.useState<string>("");
  const [saveModalOpen, setSaveModalOpen] = React.useState<boolean>(false);

  const cacheUrl = `${serverUrl}/implementations/request_cache?agent_id=${agentId}`
  const compileUrl = `${serverUrl}/implementations/compile`
  const fetchCache = () => {
    setLoading(true);
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {

        if (data.data) {
          setData({
            ...data.data
          });
        }
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      // message.error(err.message);
      setLoading(false);
    };
    fetchJSON(cacheUrl, payLoad, onSuccess, onError);
  };

  const compile = () => {
    setLoading(true);
    const payLoad = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...data,
        name: saveName,
        description: saveDesc
      })
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setData(data.data);
        setSaveModalOpen(false);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(compileUrl, payLoad, onSuccess, onError);
  };

  React.useEffect(() => {
    fetchCache();
  }, [])

  return <div className="">
    <ControlRowView
      title="Model"
      description=""
      value=""
      titleExtra={<Select placeholder="Select model" value={data.models[0]?.id}
        onChange={(value) => {
          const nextModels = cloneDeep(data.models) || [null, null];
          const selected = models.find((item) => item.id === value);
          if (selected) {

            if (nextModels.length < 1) {
              nextModels.push(null, null)
            }

            nextModels[0] = selected
          }

          setData({
            ...data,
            models: nextModels
          });
        }}
      >
        {
          models.map((item) => <Select.Option key={item.id} value={item.id}>{item.model}</Select.Option>)
        }
      </Select>}
      control={""}
    />
    <ControlRowView
      title="Training set"
      description=""
      value=""
      extra={<Select placeholder="Select collection" value={null}
        onChange={(value) => {
          const nextSets = cloneDeep(data.training_sets) || [];
          const selected = collections.find((item) => item.id === value);
          if (selected) {
            nextSets.push(selected);
          }

          setData({
            ...data,
            training_sets: nextSets
          });
        }}
      >
        {
          collections.filter(item => item.schema_id == agent.schema_id).map((item) => <Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)
        }
      </Select>}
      control={<Table
        rowKey="id"
        pagination={false}
        dataSource={data.training_sets}
        columns={[{
          title: "Name",
          dataIndex: "name"
        }, {
          title: "Description",
          dataIndex: "description"
        }, {
          dataIndex: "",
          width: 50,
          render: (_, record, index) => {
            return <div className="hidden-cell">
              <DeleteOutlined
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();

                  const nextSets = cloneDeep(data.training_sets) || [];
                  nextSets.splice(index, 1);
                  setData({
                    ...data,
                    training_sets: nextSets
                  });
                }}
              />
            </div>;
          }
        }]}
      />}
    />
    {/* <ControlRowView
      title="Development set"
      description=""
      value=""
      extra={<Select placeholder="Select collection" value={null}
        onChange={(value) => {
          const nextSets = cloneDeep(data.development_sets) || [];
          const selected = collections.find((item) => item.id === value);
          if (selected) {
            nextSets.push(selected);
          }

          setData({
            ...data,
            development_sets: nextSets
          });
        }}
      >
        {
          collections.map((item) => <Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)
        }
      </Select>}
      control={<Table
        rowKey="id"
                          pagination={false}
        dataSource={data.development_sets}
        columns={[{
          title: "Name",
          dataIndex: "name"
        }, {
          title: "Description",
          dataIndex: "description"
        }, {
          dataIndex: "",
          width: 50,
          render: (_, record, index) => {
            return <div className="hidden-cell">
              <DeleteOutlined
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();

                  const nextSets = cloneDeep(data.development_sets) || [];
                  nextSets.splice(index, 1);
                  setData({
                    ...data,
                    development_sets: nextSets
                  });
                }}
              />
            </div>;
          }
        }]}
      />}
    /> */}
    <ControlRowView
      title="Prompt strategy"
      description=""
      value=""
      titleExtra={<Select
        placeholder="Select strategy"
        value={data.prompt_strategy}
        onChange={(value) => {
          setData({
            ...data,
            prompt_strategy: value
          });
        }}
      >
        {
          ['Predict', 'ChainOfThought', 'ReAct'].map((item) => <Select.Option key={item} value={item}>{item}</Select.Option>)
        }
      </Select>}
      control=""
    />
    <ControlRowView
      title="Optimizer"
      description=""
      value=""
      titleExtra={<Select
        placeholder="Select optimizer"
        value={data.optimizer}
        onChange={(value) => {
          setData({
            ...data,
            optimizer: value
          });
        }}
      >
        {
          ['LabeledFewShot', 'BootstrapFewShot', 'BootstrapFewShotWithRandomSearch', 'BootstrapFewShotWithOptuna', 'KNNFewShot'].map((item) => <Select.Option key={item} value={item}>{item}</Select.Option>)
        }
      </Select>}
      control=""
    />
    {data.optimizer && ['BootstrapFewShot', 'BootstrapFewShotWithRandomSearch', 'BootstrapFewShotWithOptuna'].indexOf(data.optimizer) !== -1 &&
      <ControlRowView
        title="Teacher model"
        description=""
        value=""
        titleExtra={<Select placeholder="Select model" value={data.models[1]?.id}
          onChange={(value) => {
            const nextModels = cloneDeep(data.models) || [null, null];
            const selected = models.find((item) => item.id === value);
            if (selected) {

              if (nextModels.length < 1) {
                nextModels.push(null, null)
              } else if (nextModels.length === 1) {
                nextModels.push(null)
              }

              nextModels[1] = selected
            }

            setData({
              ...data,
              models: nextModels
            });
          }}
        >
          {
            models.map((item) => <Select.Option key={item.id} value={item.id}>{item.model}</Select.Option>)
          }
        </Select>}
        control={""}
      /> || ""
    }
    <ControlRowView
      title="Metric"
      description=""
      value=""
      titleExtra={<Select
        placeholder="Select metric"
        value={data.metric_id && `${data.metric_type},${data.metric_id}`}
        onChange={(value) => {

          if (!value) {
            setData({
              ...data,
              metric_id: undefined,
              metric_type: undefined
            });
            return;
          }
          const tp = value.split(',')[0];
          const id = Number(value.split(',')[1]);

          setData({
            ...data,
            metric_id: id,
            metric_type: tp as 'skill' | 'agent'
          });
        }}
      >
        {
          skills.map(item => <Select.Option key={`skill-${item.id}`} value={`skill,${item.id}`}>{item.name}</Select.Option>)
        }
        {
          agents.map(item => <Select.Option key={`agent-${item.id}`} value={`agent,${item.id}`}>{item.config?.name}</Select.Option>)
        }
      </Select>
      }
      control=""
    />
    <div className="w-full mt-4 text-right">
      {" "}

      <Button
        type="primary"
        onClick={() => {
          setSaveName("");
          setSaveDesc("");
          setSaveModalOpen(true);
        }}
        loading={loading}
      >
        Compile
      </Button>
    </div>
    <Modal
      title="Save the implementation"
      open={saveModalOpen}
      onOk={() => {
        if (!saveName) {
          message.warning("Name is required");
          return;
        }
        compile();
      }}
      onCancel={() => {
        setSaveModalOpen(false);
      }}
    >
      <ControlRowView
        title="Name"
        className=""
        description=""
        value=""
        control={
          <Input
            className="mt-2"
            placeholder="Please enter the name of the implementation"
            value={saveName}
            onChange={(e) => {
              setSaveName(e.target.value);
            }}
          />
        }
      />

      <ControlRowView
        title="Description"
        className="mt-4"
        description=""
        value={""}
        control={
          <Input
            className="mt-2"
            placeholder="Please enter the description of the implementation"
            value={saveDesc}
            onChange={(e) => {
              setSaveDesc(e.target.value);
            }}
          />
        }
      />
    </Modal>
  </div>;
}



export const ImplementationDetail = ({ implementation, setImplementation, agentId, schema, collections, skills, agents }:
  {
    implementation: IImplementation
    setImplementation: (implementation: IImplementation | null) => void;
    agentId: number;
    schema: ISchema;
    collections: ICollection[];
    skills: ISkill[];
    agents: IAgent[];
  }) => {

  const [data, setData] = React.useState<IImplementation>(implementation);
  const [hasChanged, setHasChanged] = React.useState<boolean>(false);
  const [evaluations, setEvaluations] = React.useState<IEvaluation[]>([]);
  const [openAddEvaluation, setOpenAddEvaluation] = React.useState<boolean>(false);
  const [addEvalueationCollectionId, setAddEvaluationCollectionId] = React.useState<number | null>(null);
  const [addEvalueationMetricId, setAddEvaluationMetricId] = React.useState<number | null>(null);
  const [addEvaluationMetricType, setAddEvaluationMetricType] = React.useState<'skill' | 'agent' | undefined>(undefined);
  const [saveAsName, setSaveAsName] = React.useState<string>("");
  const [saveAsOpen, setSaveAsOpen] = React.useState<boolean>(false);
  const [selectedEvaluation, setSelectedEvaluation] = React.useState<IEvaluation | null>(null);
  const [openDrawer, setOpenDrawer] = React.useState<boolean>(false);
  const [testInputs, setTestInputs] = React.useState<{ [key: string]: string }>({});
  const [testResult, setTestResult] = React.useState<{ [key: string]: string } | null>(null);

  const [loading, setLoading] = React.useState<boolean>(false);
  const serverUrl = getServerUrl();

  const listEvaluationUrl = `${serverUrl}/evaluations?agent_id=${agentId}&implementation_id=${implementation.id}`;
  const addEvaluationUrl = `${serverUrl}/evaluationss?`;
  const copyImplemantationUrl = `${serverUrl}/implementations`

  const fetchEvaluations = () => {
    setLoading(true);
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setEvaluations(data.data);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(listEvaluationUrl, payLoad, onSuccess, onError);
  };

  const addEvaluation = (evaluation: IEvaluation) => {
    setLoading(true);
    const payLoad = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(evaluation),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        fetchEvaluations();
        setOpenAddEvaluation(false);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);

      //for test
      // setEvaluations([{
      //   id: 555,
      //   agent_id: agentId,
      //   implementation_id: implementation.id,
      //   metric_id: addEvalueationMetricId || undefined,
      //   metric_type: addEvalueationMetricType,
      //   collection: collections.find((item) => item.id === addEvalueationCollectionId) || undefined
      // }]);

    };
    fetchJSON(addEvaluationUrl, payLoad, onSuccess, onError);
  }

  const test = () => {
    setLoading(true);
    const payLoad = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        implementation_id: implementation.id,
        inputs: testInputs
      }),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setTestResult(data.data.result);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(`${serverUrl}/implementations/test`, payLoad, onSuccess, onError);
  }

  const deleteEvaluation = (id: number) => {
    const deleteEvaluationUrl = `${serverUrl}/evaluations/delete?evaluation_id=${id}`;
    setLoading(true);
    const payLoad = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        fetchEvaluations();
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(deleteEvaluationUrl, payLoad, onSuccess, onError);
  }

  const copyImplementation = (implementation: IImplementation, close: any) => {
    delete (implementation.id);
    setLoading(true);
    const payLoad = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(implementation),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setImplementation(data.data);
        close();
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(copyImplemantationUrl, payLoad, onSuccess, onError);
  }

  React.useEffect(() => {
    fetchEvaluations();
  }, [implementation.id]);

  return selectedEvaluation ? <EvaluationDetail evaluation={selectedEvaluation} setEvalueation={setSelectedEvaluation}
    collections={collections} skills={skills} agents={agents} schema={schema}
  />
    : <div className="mb-2   relative">
      <Drawer
        title="Test"
        extra={<Button onClick={() => {
          test();
        }}>
          Execute
        </Button>}
        placement="right"
        closable={false}
        onClose={() => {
          setOpenDrawer(false);
        }} open={openDrawer}
      >
        <ControlRowView
          title="Inputs"
          className="mt-4"
          description=""
          value={""}
          control={
            <Table
              pagination={false}
              dataSource={schema.fields.filter((field) => field.mode === 'input')}
              columns={[{
                title: "Name",
                dataIndex: "name"
              }, {
                title: "Value",
                dataIndex: [1],
                render: (_, record) => {
                  return <Input value={testInputs[record.name]} onChange={(e) => {
                    testInputs[record.name] = e.target.value;
                  }} />;
                }
              }]}
              rowKey="name"
            />
          }
        />
        {testResult &&
          <ControlRowView
            title="Result"
            className="mt-4"
            description=""
            value={""}
            control={
              <Table
                dataSource={schema.fields}
                pagination={false}
                columns={[{
                  title: "Name",
                  dataIndex: "name"
                }, {
                  title: "Value",
                  dataIndex: "",
                  render: (_, record) => {
                    return <Input value={testResult[record.name]} />;
                  }
                }]}
                rowKey="name"
              />
            }
          /> || false
        }
      </Drawer>
      <div className="     rounded  ">
        <div className="flex mt-2 pb-2 mb-2 border-b space-between" >
          <div className="flex-1 font-semibold mb-2 ">
            <LeftOutlined onClick={() => {
              setImplementation(null);
            }} />
            {" "}
            <a>{data.name}</a>
          </div>
          {/* <Button
            type="primary"
            onClick={() => {
              setTestInputs({});
              setTestResult({});
              setOpenDrawer(!openDrawer);
            }}>Test (To remove)</Button> */}
        </div>

      </div>
      <ControlRowView
        title="Description"
        className="mt-4"
        description=""
        value={""}
        control={
          <Input
            className="mt-2"
            placeholder="Please enter the description of the implementation"
            value={data.description}
            onChange={(e) => {
              setData({
                ...data,
                description: e.target.value
              });
              setHasChanged(true);
            }}
          />}
      />
      <ControlRowView
        title="Generated prompt"
        className="mt-4"
        description=""
        value={""}
        control={
          <Input.TextArea
            className="mt-2"
            placeholder="Please edit the generated prompt of the implementation"
            value={data.generated_prompt}
            onChange={(e) => {
              setData({
                ...data,
                generated_prompt: e.target.value
              });
              setHasChanged(true);
            }}
          />}
      />

      <ControlRowView
        title="Evaluations"
        className="mt-4"
        description=""
        value={""}
        extra={<Button
          type="primary"
          onClick={() => {
            setOpenAddEvaluation(true);
            setAddEvaluationCollectionId(null);
            setAddEvaluationMetricId(null);
            setAddEvaluationMetricType(undefined);
          }}>Add</Button>}
        control={
          <Table
            pagination={false}
            dataSource={evaluations}
            onRow={(record) => ({
              onClick: () => {
                setSelectedEvaluation(record);
              }
            })}
            columns={[{
              title: "Time",
              dataIndex: "created_at"
            }, {
              title: "Collection",
              dataIndex: ["collection", "name"]
            }, {
              title: "Metric",
              dataIndex: "metric_id",
              render: (metric_id, record, index) => {
                if (record.metric_type === 'skill') {
                  return skills.find(item => item.id === metric_id)?.name;
                }

                return agents.find(item => item.id === metric_id)?.config?.name;
              }
            }, {
              dataIndex: "",
              width: 50,
              render: (_, record, index) => {
                return <div className="hidden-cell">
                  <DeleteOutlined
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();

                      if (record.id) {
                        deleteEvaluation(record.id);
                      }
                    }}
                  />
                </div>;
              }
            }]}
            rowKey="id"
          />
        }
      />
      <div className="w-full mt-4 text-right">
        <Modal open={saveAsOpen}
          title="Save as a new implementation"
          onOk={() => {
            copyImplementation({
              ...data,
              name: saveAsName
            }, () => {
              setSaveAsOpen(false);
            });
          }}
          onCancel={(close) => {
            setSaveAsOpen(false);
          }}
        >
          <div>
            <label>Name</label>
            <Input key="save-as-name" value={saveAsName}
              placeholder="new implementation name"
              onChange={(e) => {
                setSaveAsName(e.target.value);
              }}></Input>
          </div>
        </Modal>
        {" "}
        {hasChanged && (
          <Button
            type="primary"
            onClick={() => {
              setSaveAsName(`${implementation.name}_copy`);
              setSaveAsOpen(true);
            }}
            loading={loading}
          >
            {"Save as"}
          </Button>
        ) || ""}
      </div>
      <Modal title="Add an evaluation" open={openAddEvaluation}
        onCancel={() => {
          setOpenAddEvaluation(false);
        }}
        onOk={() => {
          if (!addEvalueationCollectionId || !addEvalueationMetricId) {
            message.error('Please select a collection and a metric');
            return;
          }

          addEvaluation({
            collection: collections.find(item => item.id === addEvalueationCollectionId),
            metric_id: addEvalueationMetricId,
            metric_type: addEvaluationMetricType,
            implementation_id: implementation.id,
            agent_id: agentId
          });
        }}
      >
        <ControlRowView
          title="Collection"
          className="mt-4"
          description=""
          value={""}
          control={
            <Select
              value={addEvalueationCollectionId}
              placeholder="Select a collection"
              onChange={(value) => {
                setAddEvaluationCollectionId(value);
              }}
            >
              {
                collections.map(item => <Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)
              }
            </Select>
          }
        />
        <ControlRowView
          title="Metric"
          className="mt-4"
          description=""
          value={""}
          control={
            <Select
              value={addEvalueationMetricId && `${addEvaluationMetricType},${addEvalueationMetricId}` || null}
              placeholder="Select a collection"
              onChange={(value) => {

                if (!value) {
                  setAddEvaluationMetricId(null);
                  setAddEvaluationMetricType(undefined);
                  return;
                }
                const tp = value.split(',')[0];
                const id = Number(value.split(',')[1]);

                if (tp === 'skill') {
                  setAddEvaluationMetricId(id);
                  setAddEvaluationMetricType(tp);
                } else if (tp === 'agent') {
                  setAddEvaluationMetricId(id);
                  setAddEvaluationMetricType('agent');
                } else {
                  setAddEvaluationMetricId(null);
                  setAddEvaluationMetricType(undefined);
                }
              }}
            >
              {
                skills.map(item => <Select.Option key={`skill-${item.id}`} value={`skill,${item.id}`}>{item.name}</Select.Option>)
              }
              {
                agents.map(item => <Select.Option key={`agent-${item.id}`} value={`agent,${item.id}`}>{item.config?.name}</Select.Option>)
              }
            </Select>
          }
        />
      </Modal>
    </div >;
}

export const ImplementationView = ({ agentId, models, collections, skills, agents, schemas }:
  {
    agentId: number;
    models: IModelConfig[];
    collections: ICollection[];
    skills: ISkill[];
    agents: IAgent[];
    schemas: ISchema[];
  }) => {

  const serverUrl = getServerUrl();

  const [loading, setLoading] = React.useState<boolean>(false);
  const [data, setData] = React.useState<IImplementation[]>([]);
  const [selected, setSelected] = React.useState<IImplementation | null>(null);


  const listImplementationUrl = `${serverUrl}/implementations?agent_id=${agentId}`

  const fetchImplementations = () => {
    setLoading(true);
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setData(data.data);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(listImplementationUrl, payLoad, onSuccess, onError);
  };

  const deleteImplementation = (id: number) => {

    const deleteImplementationUrl = `${serverUrl}/implementations/delete?implementation_id=${id}`

    setLoading(true);
    const payLoad = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        fetchImplementations();
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      // setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(deleteImplementationUrl, payLoad, onSuccess, onError);
  };

  React.useEffect(() => {
    fetchImplementations();

    // for test
    // setData([{
    //   id: 1,
    //   name: "Implementation 1",
    //   description: "Implementation 1 description",
    //   created_at: "2023-01-01 12:00:00",
    //   agent_id: agentId,
    //   generated_prompt: "Generated prompt",
    // }]);
  }, []);

  const getSchema = () => {
    const agent = agents.find((item) => item.id === agentId);
    return schemas.find((item) => item.id === agent?.schema_id);
  }

  return selected ? <ImplementationDetail
    implementation={selected}
    setImplementation={(next) => {
      fetchImplementations();
      setSelected(next);
    }}
    agentId={agentId}
    schema={getSchema()!}
    collections={collections}
    skills={skills}
    agents={agents}
  />
    : <div className="">
      <Table
        pagination={false}
        onRow={(record) => {
          return {
            onClick: (e: React.MouseEvent<HTMLTableRowElement>) => {
              e.preventDefault();
              e.stopPropagation();

              setSelected(record);
            },
          };
        }}
        dataSource={data}
        columns={[{
          title: "Name",
          dataIndex: "name"
        }, {
          title: "Description",
          dataIndex: "description"
        }, {
          title: "Time",
          dataIndex: "created_at"
        }, {
          dataIndex: "",
          width: 50,
          render: (_, record, index) => {
            return <div className="hidden-cell">
              <DeleteOutlined
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();

                  if (record.id) {
                    deleteImplementation(record.id);
                  }
                }}
              />
            </div>;
          }
        }]}
        rowKey="id"
      />
    </div>;
}

export const EvaluationDetail = ({ evaluation, setEvalueation, collections, skills, agents, schema }:
  {
    evaluation: IEvaluation;
    setEvalueation: (evaluation: IEvaluation | null) => void;
    collections: ICollection[];
    skills: ISkill[];
    agents: IAgent[];
    schema: ISchema;
  }) => {

  const getMetricJson = () => {
    if (evaluation.metric_type === 'skill') {
      return JSON.stringify(skills.find(item => item.id === evaluation.metric_id), null, 2);
    }

    return JSON.stringify(agents.find(item => item.id === evaluation.metric_id), null, 2);
  }

  return <div className="mb-2   relative">
    <div className="     rounded  ">
      <div className="flex mt-2 pb-2 mb-2 border-b">
        <div className="flex-1 font-semibold mb-2 ">
          <LeftOutlined onClick={() => {
            setEvalueation(null);
          }} />
          {" "}
          Evaluation detail
        </div>
      </div>
    </div>
    <ControlRowView
      title="Collection"
      className="mt-4"
      description=""
      value={""}
      control={
        <Select
          disabled
          value={evaluation.collection?.id}
        >
          {
            collections.map(item => <Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)
          }
        </Select>
      }
    />
    <ControlRowView
      title="Metric"
      className="mt-4"
      description=""
      value={""}
      control={
        <pre>{
          getMetricJson()
        }</pre>
      }
    />
    <ControlRowView
      title="Result"
      className="mt-4"
      description=""
      value={""}
      control={
        <Table
          pagination={false}
          rowKey={(_, index) => {
            return `${index}`;
          }}
          dataSource={evaluation.result}
          columns={
            schema.fields.map(field => ({
              title: field.name,
              dataIndex: field.name
            }))
          }
        />
      }
    />
  </div>
}

export const AgentViewer = ({
  agent,
  setAgent,
  schemas,
  skills,
  models,
  collections,
  agents,
  close,
}: {
  agent: IAgent | null;
  setAgent: (newAgent: IAgent) => void;
  schemas: ISchema[];
  skills: ISkill[];
  collections: ICollection[];
  models: IModelConfig[];
  agents: IAgent[];
  close: () => void;
}) => {
  let items = [
    {
      label: (
        <div className="w-full  ">
          {" "}
          {/* <BugAntIcon className="h-4 w-4 inline-block mr-1" /> */}
          Configuration
        </div>
      ),
      key: "1",
      children: (
        <div>
          {!agent?.type && (
            <AgentTypeSelector agent={agent} setAgent={setAgent} />
          )}

          {agent?.type && agent && (
            <AgentConfigView agent={agent} setAgent={setAgent} schemas={schemas} skills={skills} close={close} />
          )}
        </div>
      ),
    },
  ];
  if (agent) {
    if (agent?.id) {

      items.push({
        label: <div className="w-full  ">
          {" "}
          Compile
        </div>,
        key: "compile",
        children: <AgentCompileView agentId={agent.id} agent={agent} models={models} collections={collections} skills={skills} agents={agents} />
      })

      items.push({
        label: <div className="w-full  ">
          {" "}
          Implementation
        </div>,
        key: "implementations",
        children: <ImplementationView agentId={agent.id} models={models} collections={collections} skills={skills} agents={agents} schemas={schemas} />
      })

      // if (agent.type && agent.type === "groupchat") {
      //   items.push({
      //     label: (
      //       <div className="w-full  ">
      //         {" "}
      //         <UserGroupIcon className="h-4 w-4 inline-block mr-1" />
      //         Agents
      //       </div>
      //     ),
      //     key: "2",
      //     children: <AgentSelector agentId={agent?.id} />,
      //   });
      // }

      // items.push({
      //   label: (
      //     <div className="w-full  ">
      //       {" "}
      //       <CpuChipIcon className="h-4 w-4 inline-block mr-1" />
      //       Models
      //     </div>
      //   ),
      //   key: "3",
      //   children: <ModelSelector agentId={agent?.id} />,
      // });

      // items.push({
      //   label: (
      //     <>
      //       <BugAntIcon className="h-4 w-4 inline-block mr-1" />
      //       Skills
      //     </>
      //   ),
      //   key: "4",
      //   children: <SkillSelector agentId={agent?.id} />,
      // });
    }
  }

  return (
    <div className="text-primary">
      {/* <RenderView viewIndex={currentViewIndex} /> */}
      <Tabs
        tabBarExtraContent={{
          left: <div className="mr-4"><LeftOutlined onClick={close} /> </div>
        }}
        tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
        defaultActiveKey="1"
        items={items}
        destroyInactiveTabPane
      />
    </div>
  );
};
