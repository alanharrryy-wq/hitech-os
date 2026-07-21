"use client";

import { type FormEvent, useState } from "react";

type TaskPriority = "high" | "medium" | "low";
type TaskStatus = "open" | "in_progress" | "completed" | "cancelled";

type Task = {
  id: string;
  title: string;
  description: string | null;
  area: string;
  priority: TaskPriority;
  status: TaskStatus;
  href: string | null;
  assignedToId: string | null;
  assignedToName: string | null;
  version: number;
  dueAt: string | null;
};

type Workspace = {
  tasks: Task[];
  assignees: Array<{ id: string; displayName: string }>;
  meta: { source: "canonical_prisma" | "unavailable"; generatedAt: string; warning: string | null };
};

function labelStatus(status: TaskStatus) {
  return status === "open" ? "Abierta" : status === "in_progress" ? "En curso" : status === "completed" ? "Completada" : "Cancelada";
}

function labelPriority(priority: TaskPriority) {
  return priority === "high" ? "Alta" : priority === "medium" ? "Media" : "Baja";
}

function newIdempotencyKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  return `pc-task-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

export function OperationalTaskWorkspace({ initialWorkspace }: { initialWorkspace: Workspace }) {
  const [tasks, setTasks] = useState(initialWorkspace.tasks);
  const [status, setStatus] = useState(initialWorkspace.meta.warning ?? "");
  const [isCreating, setIsCreating] = useState(false);
  const [pendingTaskId, setPendingTaskId] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", area: "Operación", priority: "medium" as TaskPriority, assignedToId: "" });

  async function createTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setStatus("");
    try {
      const data = await readApi<{ task: Task; replayed: boolean }>(await fetch("/api/backoffice/operational-tasks", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...form, assignedToId: form.assignedToId || null, idempotencyKey: newIdempotencyKey() })
      }));
      setTasks((current) => [data.task, ...current.filter((task) => task.id !== data.task.id)]);
      setForm({ title: "", area: "Operación", priority: "medium", assignedToId: "" });
      setStatus(data.replayed ? "La solicitud ya estaba registrada; se recuperó la tarea existente." : "Tarea creada y releída desde la fuente canónica PC.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible crear la tarea.");
    } finally {
      setIsCreating(false);
    }
  }

  async function updateTask(task: Task, change: { status?: TaskStatus; assignedToId?: string | null }) {
    setPendingTaskId(task.id);
    setStatus("");
    try {
      const data = await readApi<{ task: Task }>(await fetch(`/api/backoffice/operational-tasks/${encodeURIComponent(task.id)}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ expectedVersion: task.version, ...change })
      }));
      setTasks((current) => data.task.status === "completed" || data.task.status === "cancelled"
        ? current.filter((item) => item.id !== data.task.id)
        : current.map((item) => item.id === data.task.id ? data.task : item));
      setStatus(`Tarea ${labelStatus(data.task.status).toLocaleLowerCase()} y confirmada desde la fuente canónica PC.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible actualizar la tarea.");
    } finally {
      setPendingTaskId(null);
    }
  }

  return (
    <section className="card" data-prisma-component="OperationalTaskWorkspace" data-prisma-surface="pc.dashboard.tasks">
      <div className="section-head">
        <div>
          <div className="kicker">seguimiento durable</div>
          <h2 className="section-title">Tareas operativas</h2>
          <div className="section-copy">Coordina trabajo normal del negocio. Los incidentes de soporte conservan su owner independiente.</div>
        </div>
        <span className="chip">{tasks.length} activa(s)</span>
      </div>

      {status ? <div className="alert-strip" role="status" aria-live="polite"><strong>Tareas</strong><span className="subtle">{status}</span></div> : null}

      <form className="inline-list" onSubmit={createTask} aria-label="Crear tarea operativa">
        <label className="field"><span>Tarea</span><input required minLength={3} maxLength={160} value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} /></label>
        <label className="field"><span>Área</span><input required minLength={2} maxLength={80} value={form.area} onChange={(event) => setForm((current) => ({ ...current, area: event.target.value }))} /></label>
        <label className="field"><span>Prioridad</span><select value={form.priority} onChange={(event) => setForm((current) => ({ ...current, priority: event.target.value as TaskPriority }))}><option value="high">Alta</option><option value="medium">Media</option><option value="low">Baja</option></select></label>
        <label className="field"><span>Asignar a</span><select value={form.assignedToId} onChange={(event) => setForm((current) => ({ ...current, assignedToId: event.target.value }))}><option value="">Sin asignar</option>{initialWorkspace.assignees.map((user) => <option key={user.id} value={user.id}>{user.displayName}</option>)}</select></label>
        <button className="btn btn-primary" type="submit" disabled={isCreating || initialWorkspace.meta.source !== "canonical_prisma"}>{isCreating ? "Creando…" : "Crear tarea"}</button>
      </form>

      {!tasks.length ? <p className="subtle">No hay tareas manuales abiertas para este negocio.</p> : <div className="list" aria-label="Tareas operativas activas">
        {tasks.map((task) => {
          const pending = pendingTaskId === task.id;
          return <article className="list-item" key={task.id} data-operational-task-status={task.status}>
            <div><strong>{labelPriority(task.priority)} · {task.area}</strong><div>{task.title}</div><span className="subtle">{labelStatus(task.status)} · {task.assignedToName ?? "Sin asignar"}</span></div>
            <div className="inline-list">
              <label className="sr-only" htmlFor={`assignee-${task.id}`}>Asignar {task.title}</label>
              <select id={`assignee-${task.id}`} value={task.assignedToId ?? ""} disabled={pending} onChange={(event) => void updateTask(task, { assignedToId: event.target.value || null })}><option value="">Sin asignar</option>{initialWorkspace.assignees.map((user) => <option key={user.id} value={user.id}>{user.displayName}</option>)}</select>
              {task.status === "open" ? <button className="btn btn-secondary" type="button" disabled={pending} onClick={() => void updateTask(task, { status: "in_progress" })}>Iniciar</button> : null}
              <button className="btn btn-primary" type="button" disabled={pending} onClick={() => void updateTask(task, { status: "completed" })}>{pending ? "Guardando…" : "Completar"}</button>
              <button className="btn" type="button" disabled={pending} onClick={() => void updateTask(task, { status: "cancelled" })}>Cancelar</button>
            </div>
          </article>;
        })}
      </div>}
    </section>
  );
}
