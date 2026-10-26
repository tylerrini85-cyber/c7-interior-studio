/** Runtime mesh registry: maps GLB meshes to component ids, used by selection, materials, variants, starlight and collision. */
import { createContext, useContext } from 'react';
import * as THREE from 'three';
import type { ComponentId } from '../project/schema';

export interface MeshEntry { mesh: THREE.Mesh; component: ComponentId | null; glbMaterial: string; nodeName: string; source: string; }

export class MeshRegistry {
  entries = new Map<THREE.Mesh, MeshEntry>();
  byComponent = new Map<ComponentId, Set<THREE.Mesh>>();
  byNode = new Map<string, THREE.Mesh>();
  listeners = new Set<() => void>();
  version = 0;

  register(e: MeshEntry) {
    this.entries.set(e.mesh, e);
    this.byNode.set(e.nodeName, e.mesh);
    if (e.component) {
      if (!this.byComponent.has(e.component)) this.byComponent.set(e.component, new Set());
      this.byComponent.get(e.component)!.add(e.mesh);
    }
    this.bump();
  }
  unregister(mesh: THREE.Mesh) {
    const e = this.entries.get(mesh);
    if (!e) return;
    this.entries.delete(mesh);
    if (this.byNode.get(e.nodeName) === mesh) this.byNode.delete(e.nodeName);
    if (e.component) this.byComponent.get(e.component)?.delete(mesh);
    this.bump();
  }
  private scheduled = false;
  /** Listeners are notified once per microtask, so registering hundreds of meshes yields a single notification. */
  bump() {
    this.version++;
    if (this.scheduled) return;
    this.scheduled = true;
    queueMicrotask(() => { this.scheduled = false; for (const l of [...this.listeners]) l(); });
  }
  subscribe(l: () => void) { this.listeners.add(l); return () => { this.listeners.delete(l); }; }
  meshesFor(id: ComponentId): THREE.Mesh[] { return [...(this.byComponent.get(id) ?? [])]; }
  nodesWithPrefix(prefix: string): THREE.Mesh[] { const out: THREE.Mesh[] = []; for (const [n, m] of this.byNode) if (n.startsWith(prefix)) out.push(m); return out; }
  solids(): THREE.Mesh[] { const out: THREE.Mesh[] = []; for (const e of this.entries.values()) if (!e.nodeName.startsWith('glass.') && e.mesh.visible) out.push(e.mesh); return out; }
}

export const RegistryContext = createContext<MeshRegistry | null>(null);
export function useRegistry() { const r = useContext(RegistryContext); if (!r) throw new Error('registry missing'); return r; }
