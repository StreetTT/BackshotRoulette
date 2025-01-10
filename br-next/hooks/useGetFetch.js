import { useState, useEffect } from "react";

const useGetFetch = (endpoint) => {
  const [isPending, setIsPending] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchData = async () => {
      setIsPending(true);
      try {
        const response = await fetch(endpoint, { signal: abortController.signal });
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        setData(data);
        setError(null);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setIsPending(false);
      }
    };

    fetchData();

    return () => {
      abortController.abort();
    };
  }, [endpoint]);

  return { data, isPending, error };
};

export default useGetFetch;
