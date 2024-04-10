import { useState, useEffect } from "react";

const useGetFetch = (endpoint) => {
    const [isPending, setIsPending] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [cleanupCalled, setCleanupCalled] = useState(false); // Add state to track if cleanup is called
    

    useEffect(() => {
        console.log("useGetFetch used");
        const abortCont = new AbortController();

        const fetchData = async () => {
            try {
                const res = await fetch(endpoint, { signal: abortCont.signal });
                if (!res.ok) {
                    throw Error("Data could not be fetched.");
                }
                const jsonData = await res.json();
                setData(jsonData);
                setError(null);
                setIsPending(false);
            } catch (e) {
                console.log(e.name);
                if (e.name !== 'AbortError') {
                    setError(e.message);
                    setIsPending(false);
                }
            }
        };

        fetchData();

        // Return a cleanup function that cancels the fetch request only when the component unmounts
        return () => {
            if (!cleanupCalled) { // Ensure cleanup is called only once
                abortCont.abort();
                setCleanupCalled(true);
            }
        };
    }, [endpoint]);

    return { data, isPending, error };
};

export default useGetFetch;
