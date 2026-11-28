const API_URL = import.meta.env?.VITE_API_URL || "http://127.0.0.1:8000/api/v1";
let accessToken = null;
let unauthorizedHandler = null;

export function setAccessToken(token) {
    accessToken = token;
}
export function setUnauthorizedHandler(handler) {
    unauthorizedHandler = handler;
}

function validationMessage(detail) {
    const messages = {
        missing: "Заполните обязательное поле",
        string_too_short: "Введите значение",
        string_too_long: "Превышена допустимая длина",
        int_type: "Введите целое число",
        greater_than: "Введите положительное число",
        less_than_equal: "Значение превышает допустимый предел",
        date_from_datetime_parsing: "Введите корректную дату",
        date_parsing: "Введите корректную дату",
    };

    if (detail.type === "value_error" && detail.msg?.startsWith("Value error, ")) {
        return detail.msg.slice("Value error, ".length);
    }

    return messages[detail.type] || "Проверьте введенные данные";
}

async function request(path, method = "GET", data, authenticated = true) {
    const headers = { Accept: "application/json" };
    const token = authenticated ? accessToken : null;

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    if (data !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    let response;

    try {
        response = await fetch(`${API_URL}${path}`, {
            method,
            headers,
            body: data === undefined ? undefined : JSON.stringify(data),
        });
    } catch {
        throw new Error("Не удалось подключиться к серверу");
    }

    if (response.status === 204) {
        return;
    }

    const result = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = result?.detail;
        let message = "Не удалось выполнить запрос";
        let field;

        if (typeof detail === "string") {
            message = detail;
        } else if (Array.isArray(detail) && detail.length) {
            message = validationMessage(detail[0]);
            field = detail[0].loc?.at(-1);
        } else if (detail?.message) {
            message = detail.message;
            field = detail.field;
        }
        if (response.status === 401 && token && token === accessToken) {
            setAccessToken(null);
            unauthorizedHandler?.();
        }

        const error = new Error(message);
        error.field = field;
        throw error;
    }

    return result;
}

export async function login({ email, password }) {
    return request("/sessions", "POST", { email, password }, false);
}

export async function register({ full_name, email, password }) {
    return request("/users", "POST", { full_name, email, password }, false);
}

export async function getPublicationGenres() {
    return request("/publications/genres");
}

export async function getPublications({
    search = "",
    genre = "",
    sort = "title",
    direction = "asc",
    page = 1,
    pageSize = 5,
} = {}) {
    const params = new URLSearchParams({
        search,
        genre,
        sort,
        direction,
        page,
        page_size: pageSize,
    });
    return request(`/publications?${params}`);
}

export async function getPublication(id) {
    return request(`/publications/${id}`);
}

export async function createPublication(data) {
    return request("/publications", "POST", data);
}

export async function updatePublication(id, data) {
    return request(`/publications/${id}`, "PUT", data);
}

export async function deletePublication(id) {
    return request(`/publications/${id}`, "DELETE");
}

export async function getCopies(publicationId) {
    return request(`/publications/${publicationId}/copies`);
}

export async function createCopy(publicationId, inventoryNumber) {
    return request("/copies", "POST", {
        publication_id: publicationId,
        inventory_number: inventoryNumber,
    });
}

export async function updateCopy(id, inventoryNumber) {
    return request(`/copies/${id}`, "PUT", { inventory_number: inventoryNumber });
}

export async function getReaders() {
    return request("/readers");
}

export async function updateReader(id, data) {
    return request(`/readers/${id}`, "PUT", data);
}

function loanParams({
    search = "",
    status = "",
    sort = "loan_date",
    direction = "desc",
    page = 1,
    pageSize = 10,
} = {}) {
    return new URLSearchParams({ search, status, sort, direction, page, page_size: pageSize });
}

export async function getLoans(options) {
    return request(`/loans?${loanParams(options)}`);
}

export async function getAvailableCopies() {
    return request("/copies/available");
}

export async function createLoan(data) {
    return request("/loans", "POST", data);
}

export async function returnLoan(id, returnDate) {
    return request(`/loans/${id}`, "PATCH", { return_date: returnDate });
}

export async function getMyLoans(options) {
    return request(`/loans/mine?${loanParams(options)}`);
}

export function getTodayDate() {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}
