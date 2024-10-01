import * as React from "react";
import SkillsView from "./skills";
import AgentsView from "./agents";
import WorkflowView from "./workflow";
import { Button, Tabs, message } from "antd";
import {
  BugAntIcon,
  CpuChipIcon,
  Square2StackIcon,
  Square3Stack3DIcon,

} from "@heroicons/react/24/outline";
import { RobotOutlined } from '@ant-design/icons';
import ModelsView from "./models";
import SchemasView from "./schemas";
import CollectionsView from "./collections";

const BuildView = () => {
  return (
    <div className=" ">
      {/* <div className="mb-4 text-2xl">Build </div> */}
      <div className="mb-6 text-sm hidden text-secondary">
        {" "}
        Create skills, agents and workflows for building multiagent capabilities{" "}
      </div>

      <div className="mb-4 text-primary">
        {" "}
        <Tabs
          tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
          defaultActiveKey="4"
          tabPosition="left"
          destroyInactiveTabPane
          tabBarExtraContent={<Button icon={<RobotOutlined />} onClick={() => {
            window.open("http://20.115.52.76:14042/upstream/1@1.com/docs")
          }} style={{ marginTop: 24, marginLeft: -40 }} type="link">Test</Button>}
          items={[
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <BugAntIcon className="h-4 w-4 inline-block mr-1" />
                  Functions
                </div>
              ),
              key: "1",
              children: <SkillsView />,
            },
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <CpuChipIcon className="h-4 w-4 inline-block mr-1" />
                  Models
                </div>
              ),
              key: "2",
              children: <ModelsView />,
            },
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <CpuChipIcon className="h-4 w-4 inline-block mr-1" />
                  Schemas
                </div>
              ),
              key: "2.2",
              children: <SchemasView />,
            },
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <CpuChipIcon className="h-4 w-4 inline-block mr-1" />
                  Collections
                </div>
              ),
              key: "2.3",
              children: <CollectionsView />,
            },
            {
              label: (
                <>
                  <Square2StackIcon className="h-4 w-4 inline-block mr-1" />
                  Modules
                </>
              ),
              key: "3",
              children: <AgentsView />,
            },
            {
              label: (
                <>
                  <Square3Stack3DIcon className="h-4 w-4 inline-block mr-1" />
                  Piplines
                </>
              ),
              key: "4",
              children: <WorkflowView />,
            },
          ]}
        />
      </div>

      <div></div>
    </div>
  );
};

export default BuildView;
