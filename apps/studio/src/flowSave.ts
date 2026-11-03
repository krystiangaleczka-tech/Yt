import { api } from "./api";
import { flowFrom } from "./flowTypes";
import type { FlowData } from "./flowTypes";
import type { Project } from "./types";

type Mutate = (fn: (p: Project) => Promise<Project>) => Promise<Project>;

/**
 * Persists the guided film flow through its dedicated, validated endpoint.
 * The general project PATCH intentionally refuses `legacy`, so every stage
 * (Master Story … director) must save through here. The edit runs on the latest
 * accepted revision inside the shared save queue; throwing aborts the save.
 */
export function saveFlow(mutate: Mutate, edit: (flow: FlowData, project: Project) => void): Promise<Project> {
  return mutate(async (current) => {
    const next = structuredClone(flowFrom(current));
    edit(next, current);
    return api<Project>("/projects/" + current.id + "/flow", { expected_revision: current.revision, flow: next }, "PUT");
  });
}
