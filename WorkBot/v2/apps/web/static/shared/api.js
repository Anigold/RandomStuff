const API_BASE = "/api";

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`;

        try {
            const error = await response.json();
            detail = error.detail || detail;
        } catch {
            // Ignore non-JSON error responses.
        }

        throw new Error(detail);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}