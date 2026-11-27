import library from "../data/library.json" with { type: "json" };
import initialPublications from "../data/publications.json" with { type: "json" };

const publications = structuredClone(initialPublications);
const { copies, readers, loans, users } = structuredClone(library);

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

function isCopyAvailable(copyId) {
    return !loans.some((loan) => loan.copy_id === copyId && loan.return_date === null);
}

function getCopyCounts(publicationId) {
    const publicationCopies = copies.filter((copy) => copy.publication_id === publicationId);

    return {
        total_copies: publicationCopies.length,
        available_copies: publicationCopies.filter((copy) => isCopyAvailable(copy.id)).length,
    };
}

export async function getPublicationGenres() {
    const genres = publications.map((publication) => publication.genre);

    return [...new Set(genres)].sort((a, b) => a.localeCompare(b, "ru"));
}

export async function getPublications({
    search = "",
    genre = "",
    sort = "title",
    direction = "asc",
    page = 1,
    pageSize = 5,
} = {}) {
    const query = search.trim().toLowerCase();

    const items = publications.filter((publication) => {
        const matchesSearch =
            publication.title.toLowerCase().includes(query) ||
            publication.author.toLowerCase().includes(query);

        const matchesGenre = !genre || publication.genre === genre;

        return matchesSearch && matchesGenre;
    });

    items.sort((a, b) => {
        let result;

        if (sort === "publication_year") {
            result = a.publication_year - b.publication_year;
        } else {
            result = a[sort].localeCompare(b[sort], "ru");
        }

        return direction === "desc" ? -result : result;
    });

    const start = (page - 1) * pageSize;

    return {
        items: items.slice(start, start + pageSize).map((publication) => ({
            ...publication,
            ...getCopyCounts(publication.id),
        })),
        total: items.length,
    };
}

function checkPublicationIsbn(isbn, publicationId = null) {
    if (
        isbn &&
        publications.some(
            (publication) => publication.isbn === isbn && publication.id !== publicationId,
        )
    ) {
        const error = new Error("Издание с таким ISBN уже существует");
        error.field = "isbn";
        throw error;
    }
}

export async function createPublication(data) {
    checkPublicationIsbn(data.isbn);

    const id = Math.max(0, ...publications.map((item) => item.id)) + 1;

    const publication = {
        ...data,
        id,
    };

    publications.push(publication);

    return { ...publication };
}

export async function updatePublication(id, data) {
    const publication = publications.find((item) => item.id === id);

    if (!publication) {
        throw new Error("Издание не найдено");
    }

    checkPublicationIsbn(data.isbn, id);

    Object.assign(publication, data);

    return { ...publication };
}

export async function deletePublication(id) {
    const index = publications.findIndex((publication) => publication.id === id);

    if (index === -1) {
        throw new Error("Издание не найдено");
    }

    if (copies.some((copy) => copy.publication_id === id)) {
        throw new Error("Нельзя удалить издание, имеющее экземпляры");
    }

    publications.splice(index, 1);
}

export async function getPublication(id) {
    const publication = publications.find((item) => item.id === id);

    if (!publication) {
        throw new Error("Издание не найдено");
    }

    return {
        ...publication,
        ...getCopyCounts(id),
    };
}

export async function getCopies(publicationId) {
    return copies
        .filter((copy) => copy.publication_id === publicationId)
        .map((copy) => ({
            ...copy,
            available: isCopyAvailable(copy.id),
        }));
}
function checkInventoryNumber(inventoryNumber, copyId = null) {
    if (copies.some((copy) => copy.inventory_number === inventoryNumber && copy.id !== copyId)) {
        throw new Error("Такой инвентарный номер уже существует");
    }
}

export async function createCopy(publicationId, inventoryNumber) {
    if (!publications.some((item) => item.id === publicationId)) {
        throw new Error("Издание не найдено");
    }

    checkInventoryNumber(inventoryNumber);

    const id = Math.max(0, ...copies.map((copy) => copy.id)) + 1;

    const copy = {
        id,
        publication_id: publicationId,
        inventory_number: inventoryNumber,
    };

    copies.push(copy);

    return { ...copy };
}
export async function updateCopy(id, inventoryNumber) {
    const copy = copies.find((item) => item.id === id);

    if (!copy) {
        throw new Error("Экземпляр не найден");
    }

    checkInventoryNumber(inventoryNumber, id);

    copy.inventory_number = inventoryNumber;

    return { ...copy };
}
