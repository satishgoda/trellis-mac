import type { LogEntry } from '../types';

type Props = {
  logs: LogEntry[];
};

export function LogPanel({ logs }: Props) {
  return (
    <section className="panel log-panel" aria-label="Pipeline logs">
      <div className="panel-heading">
        <h2>Logs</h2>
        <span>{logs.length} lines</span>
      </div>
      <div className="log-stream">
        {logs.length === 0 ? (
          <div className="empty-state">No logs yet.</div>
        ) : (
          logs.map((log, index) => (
            <div key={`${log.timestamp}-${index}`} className={`log-line level-${log.level}`}>
              <time>{new Date(log.timestamp).toLocaleTimeString()}</time>
              <span>{log.step_id ?? 'session'}</span>
              <p>{log.message}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
