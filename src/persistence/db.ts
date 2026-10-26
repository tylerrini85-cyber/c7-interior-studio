/** IndexedDB project repository (idb). Projects are stored as structured documents, never as screenshots alone. */
import { openDB, type IDBPDatabase } from 'idb';
import { migrate, type ProjectDoc } from '../project/schema';

const DB_NAME = 'c7-interior-studio';
const DB_VERSION = 1;

export interface ProjectSummary {
  id: string; name: string; createdAt: string; updatedAt: string; thumbnail?: string; summary: string;
}

let dbPromise: Promise<IDBPDatabase> | null = null;

function db() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(d) {
        if (!d.objectStoreNames.contains('projects')) {
          const s = d.createObjectStore('projects', { keyPath: 'id' });
          s.createIndex('updatedAt', 'updatedAt');
        }
        if (!d.objectStoreNames.contains('settings')) d.createObjectStore('settings');
      },
    });
  }
  return dbPromise;
}

export async function saveProject(doc: ProjectDoc): Promise<void> {
  const d = await db();
  await d.put('projects', doc);
}

export async function loadProject(id: string): Promise<ProjectDoc | undefined> {
  const d = await db();
  const raw = await d.get('projects', id);
  return raw ? migrate(raw) : undefined;
}

export async function deleteProject(id: string): Promise<void> {
  const d = await db();
  await d.delete('projects', id);
}

export async function listProjects(): Promise<ProjectDoc[]> {
  const d = await db();
  const all = (await d.getAll('projects')) as unknown[];
  return all.map(migrate).sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
}

export async function getSetting<T>(key: string, fallback: T): Promise<T> {
  try {
    const d = await db();
    const v = await d.get('settings', key);
    return (v as T) ?? fallback;
  } catch {
    return fallback;
  }
}

export async function setSetting<T>(key: string, value: T): Promise<void> {
  const d = await db();
  await d.put('settings', value, key);
}

export function exportProjectJson(doc: ProjectDoc): string {
  return JSON.stringify({ app: 'c7-interior-studio', exportedAt: new Date().toISOString(), project: doc }, null, 2);
}

export function parseImportedProject(text: string): ProjectDoc {
  const parsed = JSON.parse(text);
  const raw = parsed && typeof parsed === 'object' && 'project' in parsed ? parsed.project : parsed;
  return migrate(raw);
}
