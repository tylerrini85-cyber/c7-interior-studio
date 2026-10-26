import { useEffect } from 'react';
import { useStore } from '../state/store';
import { getSetting, loadProject } from '../persistence/db';
import { Landing } from '../ui/Landing';
import { Garage } from '../ui/Garage';
import { NewProject } from '../ui/NewProject';
import { Studio } from '../ui/Studio';
import { HelpPage, SettingsPage } from '../ui/Pages';
import { ErrorBoundary } from '../ui/ErrorBoundary';

export function App() {
  const route = useStore((s) => s.route);
  const project = useStore((s) => s.project);
  const setSettings = useStore((s) => s.setSettings);
  const loadProjectDoc = useStore((s) => s.loadProjectDoc);

  // bootstrap: settings + deep link (?project=id)
  useEffect(() => {
    void (async () => {
      const saved = await getSetting<Partial<ReturnType<typeof useStore.getState>['settings']>>('settings', {});
      const params = new URLSearchParams(window.location.search);
      const q = params.get('quality');
      setSettings({ ...saved, ...(q && ['ultra', 'high', 'balanced', 'mobile'].includes(q) ? { quality: q as 'ultra' | 'high' | 'balanced' | 'mobile' } : {}) });
      const id = params.get('project');
      if (id) { const doc = await loadProject(id); if (doc) loadProjectDoc(doc); }
    })();
  }, [setSettings, loadProjectDoc]);

  // warn before leaving with unsaved changes
  useEffect(() => {
    const h = (e: BeforeUnloadEvent) => { if (useStore.getState().dirty && useStore.getState().saveStatus !== 'saved') { e.preventDefault(); } };
    window.addEventListener('beforeunload', h); return () => window.removeEventListener('beforeunload', h);
  }, []);

  if (route === 'studio' && project) return <ErrorBoundary label="The studio hit a problem"><Studio /></ErrorBoundary>;
  if (route === 'garage') return <Garage />;
  if (route === 'new') return <NewProject />;
  if (route === 'settings') return <SettingsPage />;
  if (route === 'help') return <HelpPage />;
  return <Landing />;
}
