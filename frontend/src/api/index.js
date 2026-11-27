import library from "../data/library.json" with { type: "json" };

const { readers, users } = structuredClone(library);

const passwords = new Map(users.map((user) => [user.id, "demo1234"]));

export async function login({ email, password }) {
    const user = users.find((user) => user.email === email.trim().toLowerCase());

    if (!user || passwords.get(user.id) !== password) {
        throw new Error("Неверная электронная почта или пароль");
    }

    return { ...user };
}

export async function register({ full_name, email, password }) {
    email = email.trim().toLowerCase();

    if (users.some((user) => user.email === email)) {
        throw new Error("Такая электронная почта уже зарегистрирована");
    }

    const readerId = Math.max(0, ...readers.map((reader) => reader.id)) + 1;
    const userId = Math.max(0, ...users.map((user) => user.id)) + 1;

    const reader = {
        id: readerId,
        full_name: full_name.trim(),
        card_number: `ЧБ-${String(readerId).padStart(3, "0")}`,
    };

    const user = {
        id: userId,
        email,
        role: "reader",
        reader_id: readerId,
    };

    readers.push(reader);
    users.push(user);
    passwords.set(user.id, password);

    return { ...user };
}
