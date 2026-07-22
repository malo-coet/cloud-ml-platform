import { useCallback, useEffect, useState } from "react";
import { ApiError } from "./client";

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/** Runs an async loader on mount and exposes {data, loading, error, reload}. */
export function useApi<T>(loader: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // The loader identity changes every render, so key the effect on the caller's deps.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(loader, deps);

  const execute = useCallback(() => {
    let active = true;
    setLoading(true);
    setError(null);
    run()
      .then((result) => active && setData(result))
      .catch((err) => active && setError(err instanceof ApiError ? err.message : String(err)))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [run]);

  useEffect(execute, [execute]);

  return { data, loading, error, reload: execute };
}
