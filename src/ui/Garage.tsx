import { useEffect, useRef, useState } from 'react';
import { useStore } from '../state/store';
import { deleteProject, listProjects, saveProject, exportProjectJson, parseImportedProject } from '../persistence/db';
import { summarizeProject } from '../project/presets';
import { newId, type ProjectDoc } from '../project/schema';
import { Button, Modal, TextField } from './common';

export function Garage() {
  const setRoute = useStore((s) => s.setRoute);
  const loadProjectDoc = useStore((s) => s.loadProjectDoc);
  const notify = useStore((s) => s.notify);
  const [projects, setProjects] = useState<ProjectDoc[] | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<ProjectDoc | null>(null);
  const [renaming, setRenaming] = useState<ProjectDoc | null>(null);
  const [newName, setNewName] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const refresh = () => listProjects().then(setProjects).catch(() => { setProjects([]); notify('Could not read saved projects', 'error'); });
  useEffect(() => { void refresh(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const duplicate = async (p: ProjectDoc) => {
    const copy: ProjectDoc = { ...p, id: newId(), name: `${p.name} copy`, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
    await saveProject(copy); await refresh(); notify('Project duplicated', 'success');
  };
  const exportOne = (p: ProjectDoc) => {
    const blob = new Blob([exportProjectJson(p)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${p.name.replace(/[^a-z0-9-_]+/gi, '_')}.c7studio.json`; a.click(); URL.revokeObjectURL(a.href);
  };
  const importFile = async (f: File) => {
    try {
      const doc = parseImportedProject(await f.text());
      const existing = projects?.find((p) => p.id === doc.id);
      if (existing) { doc.id = newId(); doc.name = `${doc.name} (imported)`; }
      await saveProject(doc); await refresh(); notify(`Imported "${doc.name}"`, 'success');
    } catch (e) { notify('Import failed: not a valid project file', 'error'); console.error(e); }
  };

  return (
    <div className="page">
      <header className="page-head">
        <Button icon="back" title="Back" onClick={() => setRoute('menu')} /><h2>My Garage</h2>
        <div className="spacer" />
        <input ref={fileRef} type="file" accept=".json,application/json" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) void importFile(f); e.target.value = ''; }} />
        <Button icon="upload" variant="outline" onClick={() => fileRef.current?.click()}>Import</Button>
        <Button icon="plus" variant="primary" onClick={() => setRoute('new')}>New project</Button>
      </header>
      {projects === null && <p className="muted">Loading…</p>}
      {projects?.length === 0 && <div className="empty"><p>No saved designs yet.</p><Button variant="primary" icon="plus" onClick={() => setRoute('new')}>Create your first project</Button></div>}
      <div className="garage-grid">
        {projects?.map((p) => (
          <article key={p.id} className="project-card">
            <button type="button" className="thumb" onClick={() => loadProjectDoc(p)} aria-label={`Open ${p.name}`}>
              {p.thumbnail ? <img src={p.thumbnail} alt="" /> : <div className="thumb-empty">No preview yet</div>}
            </button>
            <div className="project-meta">
              <h3>{p.name}</h3>
              <p className="muted small">{summarizeProject(p)}</p>
              <p className="muted small">Created {new Date(p.createdAt).toLocaleDateString()} · Edited {new Date(p.updatedAt).toLocaleString()}</p>
              <div className="actions">
                <Button variant="primary" size="sm" icon="play" onClick={() => loadProjectDoc(p)}>Open</Button>
                <Button size="sm" icon="edit" title="Rename" onClick={() => { setRenaming(p); setNewName(p.name); }} />
                <Button size="sm" icon="copy" title="Duplicate" onClick={() => void duplicate(p)} />
                <Button size="sm" icon="download" title="Export" onClick={() => exportOne(p)} />
                <Button size="sm" icon="trash" title="Delete" variant="danger" onClick={() => setConfirmDelete(p)} />
              </div>
            </div>
          </article>
        ))}
      </div>
      {confirmDelete && (
        <Modal title="Delete project?" onClose={() => setConfirmDelete(null)}>
          <p>"{confirmDelete.name}" will be permanently deleted from this browser. Export it first if you want a backup.</p>
          <div className="form-actions"><Button onClick={() => setConfirmDelete(null)}>Cancel</Button><Button variant="danger" icon="trash" onClick={async () => { await deleteProject(confirmDelete.id); setConfirmDelete(null); await refresh(); notify('Project deleted'); }}>Delete</Button></div>
        </Modal>
      )}
      {renaming && (
        <Modal title="Rename project" onClose={() => setRenaming(null)}>
          <TextField label="Name" value={newName} onChange={setNewName} maxLength={48} />
          <div className="form-actions"><Button onClick={() => setRenaming(null)}>Cancel</Button><Button variant="primary" onClick={async () => { await saveProject({ ...renaming, name: newName.trim() || renaming.name, updatedAt: new Date().toISOString() }); setRenaming(null); await refresh(); }}>Save</Button></div>
        </Modal>
      )}
    </div>
  );
}
