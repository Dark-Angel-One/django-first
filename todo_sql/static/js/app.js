// --- CSRF Token Helper ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// --- Menu Logic ---
function toggleMenu(btn) {
    const menu = btn.nextElementSibling;
    const isOpen = !menu.classList.contains('hidden');
    closeAllMenus();
    if (!isOpen) {
        menu.classList.remove('hidden');
    }
}

function closeAllMenus() {
    document.querySelectorAll('.menu-dropdown').forEach(el => el.classList.add('hidden'));
}

document.addEventListener('click', () => closeAllMenus());

// --- State & DOM ---
// Elements will be captured when needed or we assume script is loaded at the end of body
const createNoteCollapsed = document.getElementById('create-note-collapsed');
const createNoteForm = document.getElementById('create-note-form');
const pinnedGrid = document.getElementById('pinned-notes');
const otherGrid = document.getElementById('other-notes');
const pinnedTitle = document.getElementById('pinned-title');
const othersTitle = document.getElementById('others-title');
const emptyState = document.getElementById('empty-state');
const globalSearch = document.getElementById('global-search');

// --- SortableJS ---
function initSortable() {
    if (!pinnedGrid || !otherGrid) return;

    const opts = {
        group: 'notes',
        animation: 150,
        delay: 100,
        draggable: '.note-card',
        onEnd: function (evt) {
            const item = evt.item;
            const newContainerId = item.parentElement.id;
            const isNowPinned = newContainerId === 'pinned-notes';

            updateCardPinVisuals(item, isNowPinned);
            updateSectionTitles();
            persistReorder();
        }
    };

    if (typeof Sortable !== 'undefined') {
        new Sortable(pinnedGrid, opts);
        new Sortable(otherGrid, opts);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initSortable();
    updateSectionTitles();
});

function updateCardPinVisuals(card, isPinned) {
    card.dataset.pinned = isPinned ? 'true' : 'false';
    const pinBtnIcon = card.querySelector('.absolute.top-2.right-2 button span');
    const pinContainer = card.querySelector('.absolute.top-2.right-2');

    if (isPinned) {
        pinBtnIcon.classList.add('fill-1');
        pinContainer.classList.add('opacity-100');
    } else {
        pinBtnIcon.classList.remove('fill-1');
        pinContainer.classList.remove('opacity-100');
    }
}

function updateSectionTitles() {
    if (!pinnedGrid || !otherGrid) return;
    const hasPinned = pinnedGrid.children.length > 0;

    if (hasPinned) {
        pinnedTitle.classList.remove('hidden');
        othersTitle.classList.remove('hidden');
    } else {
        pinnedTitle.classList.add('hidden');
        othersTitle.classList.add('hidden');
    }

    const pinnedContainer = document.getElementById('pinned-container');
    if (!hasPinned && pinnedContainer) pinnedContainer.classList.add('hidden');
    else if (pinnedContainer) pinnedContainer.classList.remove('hidden');

    if (emptyState) {
        if (pinnedGrid.children.length === 0 && otherGrid.children.length === 0) emptyState.style.display = 'block';
        else emptyState.style.display = 'none';
    }
}

async function persistReorder() {
    const pinnedIds = Array.from(pinnedGrid.children).map(el => parseInt(el.dataset.id));
    const otherIds = Array.from(otherGrid.children).map(el => parseInt(el.dataset.id));

    try {
        await fetch('/api/v1/notes/reorder/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ pinned_ids: pinnedIds, other_ids: otherIds })
        });
    } catch (e) {
        console.error("Reorder failed", e);
    }
}

// --- Create Note Logic ---
function showCreateNote(isChecklist = false) {
    createNoteCollapsed.classList.add('hidden');
    createNoteForm.classList.remove('hidden');

    const checklistContainer = document.getElementById('checklist-container');
    const contentInput = document.getElementById('note-content-input');
    const isChecklistInput = document.getElementById('form-is-checklist');

    if (isChecklist) {
        checklistContainer.classList.remove('hidden');
        contentInput.classList.add('hidden');
        isChecklistInput.value = 'true';
        // Add one item if empty
        if (document.getElementById('checklist-items-form').children.length === 0) {
            addChecklistItemInput();
        }
    } else {
        checklistContainer.classList.add('hidden');
        contentInput.classList.remove('hidden');
        isChecklistInput.value = 'false';
        contentInput.focus();
    }
}

function handleSaveNote() {
    // Collect data
    const title = createNoteForm.querySelector('[name="title"]').value.trim();
    const content = createNoteForm.querySelector('[name="content"]').value.trim();
    const color = document.getElementById('form-color').value;
    const isPinned = document.getElementById('form-is-pinned').value === 'true';
    const isArchived = document.getElementById('form-is-archived').value === 'true';
    const isChecklist = document.getElementById('form-is-checklist').value === 'true';
    const reminderDate = document.getElementById('form-reminder-date').value;

    let checklistItems = [];
    if (isChecklist) {
        document.querySelectorAll('.checklist-item-input').forEach((input, index) => {
            if (input.value.trim()) {
                checklistItems.push({
                    text: input.value.trim(),
                    is_checked: input.dataset.checked === 'true',
                    order: index
                });
            }
        });
    }

    const labelCheckboxes = createNoteForm.querySelectorAll('input[name="label_ids"]:checked');
    const labelIds = Array.from(labelCheckboxes).map(cb => parseInt(cb.value));

    // Only save if not empty
    if (title || content || checklistItems.length > 0) {
        saveNote({
            title, content, color, is_pinned: isPinned, is_archived: isArchived,
            is_checklist: isChecklist, checklist_items: checklistItems, label_ids: labelIds,
            reminder_date: reminderDate || null
        });
    }

    resetCreateForm();
}

function handleDiscardNote() {
    resetCreateForm();
}

function resetCreateForm() {
    createNoteForm.reset();
    // Uncheck labels
    createNoteForm.querySelectorAll('input[name="label_ids"]').forEach(cb => cb.checked = false);
    document.getElementById('checklist-items-form').innerHTML = '';
    createNoteForm.style.backgroundColor = ''; // Reset color
    document.getElementById('form-color').value = 'white';
    // Reset Pin/Archive icons
    document.querySelector('.icon-pin').classList.remove('fill-1');
    document.getElementById('form-is-pinned').value = 'false';
    document.getElementById('form-reminder-date').value = '';

    createNoteCollapsed.classList.remove('hidden');
    createNoteForm.classList.add('hidden');
}

function togglePinForm(btn) {
    const input = document.getElementById('form-is-pinned');
    const icon = btn.querySelector('.material-symbols-outlined');
    const isPinned = input.value === 'true';
    input.value = !isPinned;
    icon.classList.toggle('fill-1');
}

function toggleArchiveForm(btn) {
    const input = document.getElementById('form-is-archived');
    input.value = input.value === 'true' ? 'false' : 'true';
    btn.classList.toggle('text-gray-900'); // Simple visual feedback
}

function setFormColor(color) {
    document.getElementById('form-color').value = color;
    // Map color to tailwind class for preview
    const tailwindClassMap = {
        'white': 'bg-white', 'red': 'bg-red-100', 'orange': 'bg-orange-100', 'yellow': 'bg-yellow-100',
        'green': 'bg-green-100', 'teal': 'bg-teal-100', 'blue': 'bg-blue-100', 'darkblue': 'bg-indigo-100',
        'purple': 'bg-purple-100', 'pink': 'bg-pink-100', 'brown': 'bg-amber-100', 'gray': 'bg-gray-100'
    };
    const tailwindDarkClassMap = {
        'white': 'dark:bg-keep-bg-dark', 'red': 'dark:bg-red-900', 'orange': 'dark:bg-orange-900',
        'yellow': 'dark:bg-yellow-900', 'green': 'dark:bg-green-900', 'teal': 'dark:bg-teal-900',
        'blue': 'dark:bg-blue-900', 'darkblue': 'dark:bg-indigo-900', 'purple': 'dark:bg-purple-900',
        'pink': 'dark:bg-pink-900', 'brown': 'dark:bg-amber-900', 'gray': 'dark:bg-gray-800'
    };

    // Remove old color classes
    createNoteForm.classList.remove('bg-white', 'dark:bg-keep-bg-dark');
    // Remove all potential color classes
    const allColors = Object.values(tailwindClassMap).concat(Object.values(tailwindDarkClassMap));
    createNoteForm.classList.remove(...allColors);

    createNoteForm.classList.add(tailwindClassMap[color], tailwindDarkClassMap[color]);
}

function addChecklistItemInput(value = '', isChecked = false, insertAfterNode = null) {
    const container = document.getElementById('checklist-items-form');
    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 group/item';
    div.innerHTML = `
        <span class="material-symbols-outlined text-gray-400 cursor-pointer select-none">
            ${isChecked ? 'check_box' : 'check_box_outline_blank'}
        </span>
        <input type="text" class="checklist-item-input bg-transparent outline-none flex-1 text-sm text-gray-800 dark:text-gray-200 border-b border-transparent focus:border-gray-300 py-1"
            placeholder="Пункт списка"
            value="${value}"
            data-checked="${isChecked}">
        <span class="material-symbols-outlined text-gray-400 cursor-pointer hover:text-gray-600 opacity-0 group-hover/item:opacity-100 transition-opacity">close</span>
    `;

    if (insertAfterNode && insertAfterNode.parentNode === container) {
        if (insertAfterNode.nextSibling) {
            container.insertBefore(div, insertAfterNode.nextSibling);
        } else {
            container.appendChild(div);
        }
    } else {
        container.appendChild(div);
    }

    // Focus the new input
    div.querySelector('input').focus();
}

function handleChecklistKeydown(event, input) {
    if (event.key === 'Enter') {
        event.preventDefault();
        addChecklistItemInput('', false, input.parentElement);
    } else if (event.key === 'Backspace' && input.value === '' && document.getElementById('checklist-items-form').children.length > 1) {
        event.preventDefault();
        const prev = input.parentElement.previousElementSibling;
        input.parentElement.remove();
        if (prev) {
            const prevInput = prev.querySelector('input');
            prevInput.focus();
            // Move cursor to end
            const len = prevInput.value.length;
            prevInput.setSelectionRange(len, len);
        }
    }
}

// --- API Calls ---

async function saveNote(data) {
    try {
        const res = await fetch('/api/v1/notes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            const note = await res.json();
            prependNoteToGrid(note);
        } else {
            console.error('Failed to save', await res.json());
        }
    } catch (e) {
        console.error(e);
    }
}

// --- Grid Rendering ---

function prependNoteToGrid(note) {
    const html = createNoteCardHTML(note);
    const temp = document.createElement('div');
    temp.innerHTML = html;
    const noteNode = temp.firstElementChild;

    if (note.is_pinned) {
        pinnedGrid.prepend(noteNode);
    } else {
        otherGrid.prepend(noteNode);
    }
    updateSectionTitles();
}

function escapeHtml(text) {
    if (!text) return text;
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function createNoteCardHTML(note) {
    // Must match note_card.html logic.
    const colorClassMap = {
        'white': 'bg-white dark:bg-keep-bg-dark', 'red': 'bg-red-100 dark:bg-red-900', 'orange': 'bg-orange-100 dark:bg-orange-900',
        'yellow': 'bg-yellow-100 dark:bg-yellow-900', 'green': 'bg-green-100 dark:bg-green-900', 'teal': 'bg-teal-100 dark:bg-teal-900',
        'blue': 'bg-blue-100 dark:bg-blue-900', 'darkblue': 'bg-indigo-100 dark:bg-indigo-900', 'purple': 'bg-purple-100 dark:bg-purple-900',
        'pink': 'bg-pink-100 dark:bg-pink-900', 'brown': 'bg-amber-100 dark:bg-amber-900', 'gray': 'bg-gray-100 dark:bg-gray-800'
    };
    const bgClass = colorClassMap[note.color] || colorClassMap['white'];

    let contentHtml = '';
    if (note.is_checklist) {
        // Build checklist safely
        const ul = document.createElement('ul');
        ul.className = 'space-y-1';

        note.checklist_items.slice(0, 5).forEach(item => {
            const li = document.createElement('li');
            li.className = 'flex items-start gap-2 text-sm text-gray-800 dark:text-gray-200';

            const spanIcon = document.createElement('span');
            spanIcon.className = 'material-symbols-outlined text-[18px] text-gray-400 cursor-pointer';
            spanIcon.onclick = function(e) { e.stopPropagation(); toggleCheckbox(item.id, this); };
            spanIcon.textContent = item.is_checked ? 'check_box' : 'check_box_outline_blank';

            const spanText = document.createElement('span');
            spanText.className = item.is_checked ? 'line-through text-gray-500 break-all' : 'break-all';
            spanText.textContent = item.text;

            li.appendChild(spanIcon);
            li.appendChild(spanText);
            ul.appendChild(li);
        });

        if (note.checklist_items.length > 5) {
            const liMore = document.createElement('li');
            liMore.className = 'text-xs text-gray-500 pl-7';
            // Translated
            liMore.textContent = `+ ещё ${note.checklist_items.length - 5}`;
            ul.appendChild(liMore);
        }
        contentHtml = ul.outerHTML;
    } else {
        // Build text content safely
        const p = document.createElement('p');
        p.className = 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden';
        p.textContent = note.content.substring(0, 300);
        contentHtml = p.outerHTML;
    }

    let labelsHtml = '';
    if (note.labels && note.labels.length > 0) {
        labelsHtml = '<div class="flex flex-wrap gap-1 mt-2">';
        note.labels.forEach(l => {
            labelsHtml += `<span class="px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-xs text-gray-700 dark:text-gray-300 cursor-pointer" onclick="event.stopPropagation(); window.location.href='/label/${l.name}/'">${l.name}</span>`;
        });
        labelsHtml += '</div>';
    }

    return `
    <div class="note-card relative group rounded-lg border border-gray-200 dark:border-gray-700 p-4 transition-all hover:shadow-md cursor-default flex flex-col justify-between ${bgClass}" data-id="${note.id}" data-pinned="${note.is_pinned}" data-reminder="${note.reminder_date || ''}">
        <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 ${note.is_pinned ? 'opacity-100' : ''} transition-opacity z-20">
            <button onclick="event.stopPropagation(); togglePinNote(${note.id})" class="p-1 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-gray-700 dark:text-gray-300">
                <span class="material-symbols-outlined text-[20px] ${note.is_pinned ? 'fill-1' : ''}">keep</span>
            </button>
        </div>
        <div onclick="openEditModal(${note.id})" class="cursor-pointer flex-1">
            ${note.title ? `<h3 class="font-medium text-lg mb-2 text-gray-900 dark:text-gray-100 break-words pr-6">${escapeHtml(note.title)}</h3>` : ''}
            ${contentHtml}
            ${labelsHtml}
        </div>
        <div class="flex justify-between items-center mt-4 opacity-0 group-hover:opacity-100 transition-opacity h-8">
            <div class="flex gap-1">
                <button class="p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-gray-600 dark:text-gray-300" title="Archive" onclick="event.stopPropagation(); archiveNote(${note.id})">
                    <span class="material-symbols-outlined text-[18px]">archive</span>
                </button>
                <button class="p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-gray-600 dark:text-gray-300" title="Trash" onclick="event.stopPropagation(); trashNote(${note.id})">
                    <span class="material-symbols-outlined text-[18px]">delete</span>
                </button>
            </div>
        </div>
    </div>
    `;
}

// --- Actions ---

async function performOptimisticRemove(id, apiPromise) {
    const card = document.querySelector(`.note-card[data-id="${id}"]`);
    if(!card) return;

    // Save state for rollback
    const parent = card.parentNode;
    const nextSibling = card.nextSibling;

    // Optimistic Remove
    card.remove();

    try {
        const res = await apiPromise();
        // 404 is success (idempotent), 2xx is success
        if (!res.ok && res.status !== 404) {
                throw new Error(`Failed with status ${res.status}`);
        }
    } catch (e) {
        console.error(e);
        // Restore
        if (nextSibling) {
            parent.insertBefore(card, nextSibling);
        } else {
            parent.appendChild(card);
        }
        showToast("Ошибка действия");
    }
}

function archiveNote(id) {
    performOptimisticRemove(id, () =>
        fetch(`/api/v1/notes/${id}/archive/`, { method: 'POST', headers: {'X-CSRFToken': csrftoken} })
    );
}

function trashNote(id) {
    performOptimisticRemove(id, () =>
        fetch(`/api/v1/notes/${id}/trash/`, { method: 'POST', headers: {'X-CSRFToken': csrftoken} })
    );
}

function deleteNoteForever(id) {
    performOptimisticRemove(id, () =>
        fetch(`/api/v1/notes/${id}/`, { method: 'DELETE', headers: {'X-CSRFToken': csrftoken} })
    );
}

async function togglePinNote(id) {
    const card = document.querySelector(`.note-card[data-id="${id}"]`);
    if(!card) return;

    const wasPinned = card.dataset.pinned === 'true';
    const newPinned = !wasPinned;

    updateCardPinVisuals(card, newPinned);

    if (newPinned) {
        pinnedGrid.prepend(card);
    } else {
        otherGrid.prepend(card);
    }
    updateSectionTitles();

    try {
        const res = await fetch(`/api/v1/notes/${id}/pin/`, {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken}
        });
        if(!res.ok) throw new Error('Failed');
    } catch (e) {
        console.error("Pin failed", e);
        // Rollback
        updateCardPinVisuals(card, wasPinned);
        if (wasPinned) {
            pinnedGrid.prepend(card);
        } else {
            otherGrid.prepend(card);
        }
        updateSectionTitles();
        showToast("Не удалось закрепить");
    }
}

async function toggleCheckbox(itemId, span) {
    // Toggle UI immediately
    const isChecked = span.textContent.trim() === 'check_box';
    const newStatus = !isChecked;

    span.textContent = newStatus ? 'check_box' : 'check_box_outline_blank';
    const textSpan = span.nextElementSibling;
    if(newStatus) textSpan.classList.add('line-through', 'text-gray-500');
    else textSpan.classList.remove('line-through', 'text-gray-500');

    // Call API
    await fetch(`/api/v1/checklist-items/${itemId}/`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
        body: JSON.stringify({is_checked: newStatus})
    });
}

// --- Live Search & Pagination ---
let searchTimeout;
if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadNotes(e.target.value);
        }, 300);
    });
}

async function loadNotes(urlOrQuery) {
    let url;
    if (urlOrQuery && (urlOrQuery.startsWith('/') || urlOrQuery.startsWith('http'))) {
        url = urlOrQuery;
    } else {
        url = urlOrQuery ? `/api/v1/notes/?search=${urlOrQuery}` : '/api/v1/notes/';
    }

    try {
        const res = await fetch(url);
        const data = await res.json();

        pinnedGrid.innerHTML = '';
        otherGrid.innerHTML = '';

        const notes = data.results || data;

        if (notes.length === 0 && url.includes('search=')) {
                otherGrid.innerHTML = '<div class="col-span-full text-center text-gray-500 py-10">Ничего не найдено</div>';
        } else {
            [...notes].reverse().forEach(note => prependNoteToGrid(note));
        }
        updateSectionTitles();
        renderPagination(data);
    } catch (e) {
        console.error("Failed to load notes", e);
    }
}

function renderPagination(data) {
    const container = document.getElementById('pagination-container');
    if (!container) return;

    if (!data.next && !data.previous) {
        container.innerHTML = '';
        return;
    }

    // Calculate current page.
    // If next is present, page is next_page - 1.
    // If previous is present, page is prev_page + 1.
    // next/prev urls are like ...?page=X...
    let currentPage = 1;
    if (data.next) {
        const match = data.next.match(/page=(\d+)/);
        if (match) currentPage = parseInt(match[1]) - 1;
        else currentPage = 1;
    } else if (data.previous) {
        const match = data.previous.match(/page=(\d+)/);
        if (match) currentPage = parseInt(match[1]) + 1;
        else currentPage = 2;
    }

    // Total pages
    // data.count is total items. page_size is 12 (default).
    const pageSize = 12;
    const totalPages = Math.ceil(data.count / pageSize);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    const prevDisabled = !data.previous;
    const nextDisabled = !data.next;

    // Helper for button/span
    const createBtn = (isNext, url, disabled) => {
        if (disabled) {
            return `
                <span class="p-2 text-gray-400 dark:text-gray-600 cursor-not-allowed">
                    <span class="material-symbols-outlined text-xl">${isNext ? 'chevron_right' : 'chevron_left'}</span>
                </span>
            `;
        } else {
            // We use onclick
            return `
                <a href="${url}" onclick="event.preventDefault(); loadNotes('${url}')" class="p-2 rounded-lg hover:bg-white/50 dark:hover:bg-white/10 text-gray-700 dark:text-gray-200 transition-colors" aria-label="${isNext ? 'Next' : 'Previous'}">
                    <span class="material-symbols-outlined text-xl">${isNext ? 'chevron_right' : 'chevron_left'}</span>
                </a>
            `;
        }
    };

    const html = `
        <div class="flex justify-center mt-8 pb-4">
            <nav class="inline-flex items-center p-1 rounded-xl bg-white/30 dark:bg-black/30 backdrop-blur-md border border-white/20 dark:border-white/10 shadow-lg">
                ${createBtn(false, data.previous, prevDisabled)}
                <span class="px-4 py-2 text-sm font-medium text-gray-800 dark:text-gray-200">
                    Страница ${currentPage} из ${totalPages}
                </span>
                ${createBtn(true, data.next, nextDisabled)}
            </nav>
        </div>
    `;

    container.innerHTML = html;
}

// --- Edit Modal ---
async function openEditModal(id) {
    const res = await fetch(`/api/v1/notes/${id}/`);
    const note = await res.json();
    const modal = document.getElementById('edit-modal');
    const content = document.getElementById('edit-modal-content');

    // Clear content
    content.innerHTML = '';

    // Helper to create element
    const el = (tag, classes = '', props = {}) => {
        const e = document.createElement(tag);
        if(classes) e.className = classes;
        for(const [k, v] of Object.entries(props)) {
            if(k === 'dataset') {
                for(const [dk, dv] of Object.entries(v)) e.dataset[dk] = dv;
            } else {
                e[k] = v;
            }
        }
        return e;
    };

    // Header (Title + Pin)
    const header = el('div', 'flex justify-between items-start mb-2');
    const titleInput = el('input', 'w-full bg-transparent outline-none text-lg font-medium placeholder-gray-500 text-gray-800 dark:text-gray-200', {
        type: 'text', placeholder: 'Заголовок', id: 'edit-title', value: note.title
    });

    const pinBtn = el('button', 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 p-1 rounded-full', {type: 'button'});
    pinBtn.onclick = () => toggleEditPin(pinBtn);
    const pinIcon = el('span', `material-symbols-outlined icon-pin ${note.is_pinned ? 'fill-1' : ''}`);
    pinIcon.textContent = 'keep';
    pinBtn.appendChild(pinIcon);

    const isPinnedInput = el('input', '', {type: 'hidden', id: 'edit-is-pinned', value: note.is_pinned});

    header.append(titleInput, pinBtn, isPinnedInput);
    content.append(header);

    // Content (Textarea or Checklist)
    if (note.is_checklist) {
            const checklistContainer = el('div', 'space-y-2 mb-2', {id: 'edit-checklist-container'});
            const itemsContainer = el('div', '', {id: 'edit-checklist-items-form'});

            // Sort items by order
            note.checklist_items.sort((a,b) => a.order - b.order).forEach(item => {
                itemsContainer.appendChild(createChecklistItemElement(item.text, item.is_checked, item.id));
            });

            const addBtn = el('div', 'flex items-center gap-2 text-gray-500 cursor-pointer p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded');
            addBtn.onclick = () => addChecklistItemInputEdit();
            addBtn.innerHTML = '<span class="material-symbols-outlined text-sm">add</span><span class="text-sm">Пункт списка</span>';

            checklistContainer.append(itemsContainer, addBtn);
            content.append(checklistContainer);

            // Hidden content input for compatibility
            content.append(el('textarea', 'hidden', {id: 'edit-content'}));
    } else {
        const textarea = el('textarea', 'w-full bg-transparent outline-none resize-none overflow-hidden placeholder-gray-500 text-sm text-gray-800 dark:text-gray-200 min-h-[100px]', {
            id: 'edit-content', placeholder: 'Заметка', value: note.content
        });
        content.append(textarea);
    }

    // Footer Actions
    const footer = el('div', 'flex justify-between items-center mt-4');
    const actionsLeft = el('div', 'flex gap-1 text-gray-600 dark:text-gray-400 items-center');

    // Color Picker
    const colorWrapper = el('div', 'relative');
    const colorBtn = el('button', 'p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700', {type: 'button', title: 'Color'});
    colorBtn.onclick = (e) => { e.stopPropagation(); toggleMenu(colorBtn); };
    colorBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">palette</span>';

    const colorMenu = el('div', 'absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg p-2 flex gap-1 hidden menu-dropdown border dark:border-gray-700 z-20 flex-wrap w-48');
    colorMenu.onclick = (e) => e.stopPropagation();
    ['white','red','orange','yellow','green','teal','blue','darkblue','purple','pink','brown','gray'].forEach(c => {
        const circle = el('div', `w-6 h-6 rounded-full border cursor-pointer ${getColorClass(c)}`);
        circle.onclick = () => setEditColor(c);
        colorMenu.appendChild(circle);
    });
    colorWrapper.append(colorBtn, colorMenu);
    actionsLeft.append(colorWrapper);

    // Hidden Inputs
    content.append(el('input', '', {type: 'hidden', id: 'edit-color', value: note.color}));
    content.append(el('input', '', {type: 'hidden', id: 'edit-is-archived', value: note.is_archived}));
    content.append(el('input', '', {type: 'hidden', id: 'edit-is-checklist', value: note.is_checklist}));

    // Labels
    const labelWrapper = el('div', 'relative');
    const labelBtn = el('button', 'p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700', {type: 'button', title: 'Labels'});
    labelBtn.onclick = (e) => { e.stopPropagation(); toggleMenu(labelBtn); };
    labelBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">label</span>';

    const labelMenu = el('div', 'absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg p-2 hidden menu-dropdown border dark:border-gray-700 z-20 w-48 max-h-48 overflow-y-auto');
    labelMenu.onclick = (e) => e.stopPropagation();

    // Use window.userLabels
    const userLabels = window.userLabels || [];

    userLabels.forEach(label => {
        const isChecked = note.labels.some(l => l.id === label.id);
        const lLabel = el('label', 'flex items-center gap-2 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer');
        const lInput = el('input', 'form-checkbox text-yellow-500 rounded focus:ring-0', {
            type: 'checkbox', name: 'edit_label_ids', value: label.id, checked: isChecked
        });
        const lSpan = el('span', 'text-sm text-gray-800 dark:text-gray-200 truncate');
        lSpan.textContent = label.name;
        lLabel.append(lInput, lSpan);
        labelMenu.appendChild(lLabel);
    });
    labelWrapper.append(labelBtn, labelMenu);
    actionsLeft.append(labelWrapper);

    // Archive
    const archiveBtn = el('button', `p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 ${note.is_archived ? 'text-gray-900 bg-gray-200 dark:bg-gray-600' : ''}`, {type: 'button'});
    archiveBtn.onclick = () => toggleEditArchive(archiveBtn);
    archiveBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">archive</span>';
    actionsLeft.append(archiveBtn);

    // Reminder
    const remindWrapper = el('div', 'relative');
    const remindBtn = el('button', 'p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700', {type: 'button'});
    remindBtn.onclick = (e) => { e.stopPropagation(); toggleMenu(remindBtn); };
    remindBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">notifications</span>';

    const remindMenu = el('div', 'absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg p-2 hidden menu-dropdown border dark:border-gray-700 z-20 w-64');
    remindMenu.onclick = (e) => e.stopPropagation();
    const remindInput = el('input', 'w-full bg-gray-100 dark:bg-gray-700 border-none rounded p-2 text-sm text-gray-800 dark:text-gray-200 outline-none', {
        type: 'datetime-local', id: 'edit-reminder-date', value: note.reminder_date ? note.reminder_date.slice(0, 16) : ''
    });
    remindMenu.appendChild(remindInput);
    remindWrapper.append(remindBtn, remindMenu);
    actionsLeft.append(remindWrapper);

    footer.append(actionsLeft);

    // Done Button
    const doneBtn = el('button', 'px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded text-gray-800 dark:text-gray-200', {type: 'button'});
    doneBtn.textContent = 'Готово';
    doneBtn.onclick = () => saveEditedNote(id);
    footer.append(doneBtn);

    content.append(footer);

    setEditColor(note.color);
    modal.classList.remove('hidden');
}

function createChecklistItemElement(text, isChecked, id=null) {
    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 group/item';
    div.innerHTML = `
        <span class="material-symbols-outlined text-gray-400 cursor-pointer select-none">
            ${isChecked ? 'check_box' : 'check_box_outline_blank'}
        </span>
        <input type="text" class="edit-checklist-item-input bg-transparent outline-none flex-1 text-sm text-gray-800 dark:text-gray-200 border-b border-transparent focus:border-gray-300 py-1"
            placeholder="Пункт списка"
            value="">
        <span class="material-symbols-outlined text-gray-400 cursor-pointer hover:text-gray-600 opacity-0 group-hover/item:opacity-100 transition-opacity">close</span>
    `;
    // Safe value assignment
    const input = div.querySelector('input');
    input.value = text;
    if(id) input.dataset.id = id;
    input.dataset.checked = isChecked;
    return div;
}

// --- Event Delegation ---
document.addEventListener('DOMContentLoaded', () => {
    // Create Note Form Delegation
    const checklistItemsForm = document.getElementById('checklist-items-form');
    if(checklistItemsForm) {
        checklistItemsForm.addEventListener('click', (e) => {
            const target = e.target;
            if(target.matches('.material-symbols-outlined')) {
                    const item = target.closest('.group\\/item');
                    if(item) {
                        // Checkbox
                        if(target === item.firstElementChild) {
                            const input = item.querySelector('input');
                            const isChecked = input.dataset.checked === 'true';
                            input.dataset.checked = !isChecked;
                            target.textContent = !isChecked ? 'check_box' : 'check_box_outline_blank';
                        }
                        // Close
                        if(target === item.lastElementChild) {
                            item.remove();
                        }
                    }
            }
        });
        checklistItemsForm.addEventListener('keydown', (e) => {
            if(e.target.matches('.checklist-item-input')) {
                handleChecklistKeydown(e, e.target);
            }
        });
    }

    // Edit Modal Delegation
    const editModalContent = document.getElementById('edit-modal-content');
    if(editModalContent) {
        editModalContent.addEventListener('click', (e) => {
            const target = e.target;
            if(target.matches('.material-symbols-outlined')) {
                    const item = target.closest('.group\\/item');
                    if(item) {
                        // Checkbox
                        if(target === item.firstElementChild) {
                            const input = item.querySelector('input');
                            const isChecked = input.dataset.checked === 'true';
                            input.dataset.checked = !isChecked;
                            target.textContent = !isChecked ? 'check_box' : 'check_box_outline_blank';
                        }
                        // Close
                        if(target === item.lastElementChild) {
                            item.remove();
                        }
                    }
            }
        });
        editModalContent.addEventListener('keydown', (e) => {
            if(e.target.matches('.edit-checklist-item-input')) {
                handleChecklistKeydownEdit(e, e.target);
            }
        });
    }
});

function addChecklistItemInputEdit(value='', isChecked=false, insertAfterNode=null) {
    const container = document.getElementById('edit-checklist-items-form');
    const el = createChecklistItemElement(value, isChecked);
    if (insertAfterNode && insertAfterNode.parentNode === container) {
        if (insertAfterNode.nextSibling) {
            container.insertBefore(el, insertAfterNode.nextSibling);
        } else {
            container.appendChild(el);
        }
    } else {
        container.appendChild(el);
    }
    el.querySelector('input').focus();
}

function handleChecklistKeydownEdit(event, input) {
    if (event.key === 'Enter') {
        event.preventDefault();
        addChecklistItemInputEdit('', false, input.parentElement);
    } else if (event.key === 'Backspace' && input.value === '' && document.getElementById('edit-checklist-items-form').children.length > 1) {
        event.preventDefault();
        const prev = input.parentElement.previousElementSibling;
        input.parentElement.remove();
        if (prev) {
            const prevInput = prev.querySelector('input');
            prevInput.focus();
            const len = prevInput.value.length;
            prevInput.setSelectionRange(len, len);
        }
    }
}

function closeEditModal(e) {
    if(e.target.id === 'edit-modal') {
            document.getElementById('edit-modal').classList.add('hidden');
    }
}

async function saveEditedNote(id) {
    const title = document.getElementById('edit-title').value;
    const content = document.getElementById('edit-content') ? document.getElementById('edit-content').value : '';
    const isPinned = document.getElementById('edit-is-pinned').value === 'true';
    const isArchived = document.getElementById('edit-is-archived').value === 'true';
    const isChecklist = document.getElementById('edit-is-checklist').value === 'true';
    const color = document.getElementById('edit-color').value;
    const reminderDate = document.getElementById('edit-reminder-date').value;

    const labelCheckboxes = document.querySelectorAll('input[name="edit_label_ids"]:checked');
    const labelIds = Array.from(labelCheckboxes).map(cb => parseInt(cb.value));

    let checklistItems = [];
    if (isChecklist) {
        document.querySelectorAll('#edit-checklist-items-form .edit-checklist-item-input').forEach((input, index) => {
            if(input.value.trim()) {
                checklistItems.push({
                    text: input.value.trim(),
                    is_checked: input.dataset.checked === 'true',
                    order: index,
                    id: input.dataset.id ? parseInt(input.dataset.id) : undefined
                });
            }
        });
    }

    await fetch(`/api/v1/notes/${id}/`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            title, content, is_pinned: isPinned, is_archived: isArchived,
            color, reminder_date: reminderDate || null, label_ids: labelIds,
            checklist_items: isChecklist ? checklistItems : undefined
        })
    });

    document.getElementById('edit-modal').classList.add('hidden');
    loadNotes(globalSearch.value);
}

function toggleEditPin(btn) {
    const input = document.getElementById('edit-is-pinned');
    const icon = btn.querySelector('.material-symbols-outlined');
    input.value = input.value === 'true' ? 'false' : 'true';
    icon.classList.toggle('fill-1');
}

function toggleEditArchive(btn) {
    const input = document.getElementById('edit-is-archived');
    input.value = input.value === 'true' ? 'false' : 'true';
    btn.classList.toggle('text-gray-900');
    btn.classList.toggle('bg-gray-200');
}

function setEditColor(color) {
    document.getElementById('edit-color').value = color;
    const form = document.getElementById('edit-modal-content');

    const tailwindClassMap = {
        'white': 'bg-white', 'red': 'bg-red-100', 'orange': 'bg-orange-100', 'yellow': 'bg-yellow-100',
        'green': 'bg-green-100', 'teal': 'bg-teal-100', 'blue': 'bg-blue-100', 'darkblue': 'bg-indigo-100',
        'purple': 'bg-purple-100', 'pink': 'bg-pink-100', 'brown': 'bg-amber-100', 'gray': 'bg-gray-100'
    };
    const tailwindDarkClassMap = {
        'white': 'dark:bg-keep-bg-dark', 'red': 'dark:bg-red-900', 'orange': 'dark:bg-orange-900',
        'yellow': 'dark:bg-yellow-900', 'green': 'dark:bg-green-900', 'teal': 'dark:bg-teal-900',
        'blue': 'dark:bg-blue-900', 'darkblue': 'dark:bg-indigo-900', 'purple': 'dark:bg-purple-900',
        'pink': 'dark:bg-pink-900', 'brown': 'dark:bg-amber-900', 'gray': 'dark:bg-gray-800'
    };

    form.classList.remove('bg-white', 'dark:bg-keep-bg-dark');
    const allColors = Object.values(tailwindClassMap).concat(Object.values(tailwindDarkClassMap));
    form.classList.remove(...allColors);

    form.classList.add(tailwindClassMap[color], tailwindDarkClassMap[color]);
}

function getColorClass(c) {
    const map = {'white': 'bg-white', 'red': 'bg-red-200', 'orange': 'bg-orange-200', 'yellow': 'bg-yellow-200', 'green': 'bg-green-200', 'teal': 'bg-teal-200', 'blue': 'bg-blue-200', 'darkblue': 'bg-indigo-200', 'purple': 'bg-purple-200', 'pink': 'bg-pink-200', 'brown': 'bg-amber-200', 'gray': 'bg-gray-200'};
    return map[c];
}

// --- Active Reminders ---
// Use window.staticAudioUrl or fallback
const notificationSound = new Audio(window.staticAudioUrl || "https://codeskulptor-demos.commondatastorage.googleapis.com/pang/pop.mp3");

function checkReminders() {
    const now = new Date();
    document.querySelectorAll('.note-card[data-reminder]').forEach(card => {
        const reminderStr = card.dataset.reminder;
        if (!reminderStr) return;

        const reminderDate = new Date(reminderStr);
        // Check if valid date and past/now (and not checked recently? - no, we archive it, so it's fine)
        if (!isNaN(reminderDate.getTime()) && reminderDate <= now) {
            triggerReminder(card);
        }
    });
}

async function triggerReminder(card) {
    // Prevent double firing if interval overlaps with async operations (though card removal handles this)
    if (card.dataset.processing) return;
    card.dataset.processing = "true";

    const id = card.dataset.id;
    const titleElement = card.querySelector('h3');
    const title = titleElement ? titleElement.innerText : 'Note';

    // 1. Play Sound
    try {
        await notificationSound.play();
    } catch(e) { console.log("Audio play blocked (user interaction required)", e); }

    // 2. Notification
    const msg = `Напоминание: "${title}" перемещено в архив`;
    if (Notification.permission === "granted") {
        new Notification("Todo App", { body: msg });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification("Todo App", { body: msg });
            }
        });
    }

    // 3. Toast
    showToast(msg);

    // 4. Archive (removes from grid)
    await archiveNote(id);
}

function showToast(message) {
    const div = document.createElement('div');
    div.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-xl z-50 transition-opacity duration-500 flex items-center gap-2';
    div.innerHTML = `<span class="material-symbols-outlined">notifications_active</span><span>${message}</span>`;
    document.body.appendChild(div);
    setTimeout(() => {
        div.style.opacity = '0';
        setTimeout(() => div.remove(), 500);
    }, 4000);
}

// Check every 30 seconds
setInterval(checkReminders, 30000);
// Initial request for permission
if (Notification.permission !== "granted" && Notification.permission !== "denied") {
    document.addEventListener('click', () => {
        Notification.requestPermission();
    }, { once: true });
}
