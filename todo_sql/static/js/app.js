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

function toggleMenu(btn) {
    const menu = btn.nextElementSibling;
    const isOpen = !menu.classList.contains('hidden');
    closeAllMenus();
    if (!isOpen) {
        menu.classList.remove('hidden');
        menu.classList.add('animate-fade-in-up');
    }
}

function closeAllMenus() {
    document.querySelectorAll('.menu-dropdown').forEach(el => el.classList.add('hidden'));
}
document.addEventListener('click', () => closeAllMenus());

const createNoteCollapsed = document.getElementById('create-note-collapsed');
const createNoteForm = document.getElementById('create-note-form');
const pinnedGrid = document.getElementById('pinned-notes');
const otherGrid = document.getElementById('other-notes');
const pinnedTitle = document.getElementById('pinned-title');
const othersTitle = document.getElementById('others-title');
const emptyState = document.getElementById('empty-state');
const globalSearch = document.getElementById('global-search');

function initSortable() {
    if (!pinnedGrid || !otherGrid) return;
    const opts = {
        group: 'notes', animation: 150, delay: 100, draggable: '.note-card',
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
        new Sortable(pinnedGrid, opts); new Sortable(otherGrid, opts);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initSortable(); 
    updateSectionTitles();


    // --- ЛОГИКА ТЕМЫ (СВЕТЛАЯ/ТЕМНАЯ) ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        const updateThemeIcon = () => {
            const isDark = document.documentElement.classList.contains('dark');
            const icon = themeToggleBtn.querySelector('span');
            if (icon) icon.textContent = isDark ? 'light_mode' : 'dark_mode';
            
            const metaThemeColor = document.querySelector('meta[name="theme-color"]');
            if (metaThemeColor) metaThemeColor.setAttribute('content', isDark ? '#202124' : '#ffffff');
        };

        updateThemeIcon();

        // Убираем старые конфликты и делаем чистый клик
        themeToggleBtn.onclick = function(e) {
            e.preventDefault();
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeIcon();
        };
    }

    // --- ЛОГИКА СМЕНЫ ВИДА (GRID/LIST) ---
    const viewToggleBtn = document.getElementById('view-toggle');
    if (viewToggleBtn) {
        const icon = viewToggleBtn.querySelector('span');
        let isListView = localStorage.getItem('isListView') === 'true';
        
        const applyView = () => {
            if (!pinnedGrid || !otherGrid) return;
            if (isListView) {
                pinnedGrid.classList.remove('bento-grid'); pinnedGrid.classList.add('list-view');
                otherGrid.classList.remove('bento-grid'); otherGrid.classList.add('list-view');
                icon.textContent = 'grid_view'; 
            } else {
                pinnedGrid.classList.add('bento-grid'); pinnedGrid.classList.remove('list-view');
                otherGrid.classList.add('bento-grid'); otherGrid.classList.remove('list-view');
                icon.textContent = 'view_list'; 
            }
        };
        
        applyView(); 
        
        viewToggleBtn.addEventListener('click', () => {
            isListView = !isListView;
            localStorage.setItem('isListView', isListView);
            applyView();
        });
    }
});

function updateCardPinVisuals(card, isPinned) {
    card.dataset.pinned = isPinned ? 'true' : 'false';
    const pinBtnIcon = card.querySelector('.absolute.top-2.right-2 button span');
    const pinContainer = card.querySelector('.absolute.top-2.right-2');
    if (isPinned) { pinBtnIcon.classList.add('fill-1'); pinContainer.classList.add('opacity-100'); } 
    else { pinBtnIcon.classList.remove('fill-1'); pinContainer.classList.remove('opacity-100'); }
}

function updateSectionTitles() {
    if (!pinnedGrid || !otherGrid) return;
    const hasPinned = pinnedGrid.children.length > 0;
    if (hasPinned) { pinnedTitle.classList.remove('hidden'); othersTitle.classList.remove('hidden'); } 
    else { pinnedTitle.classList.add('hidden'); othersTitle.classList.add('hidden'); }

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
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            body: JSON.stringify({ pinned_ids: pinnedIds, other_ids: otherIds })
        });
    } catch (e) { console.error("Reorder failed", e); }
}

function showCreateNote(isChecklist = false) {
    createNoteCollapsed.classList.add('hidden');
    createNoteForm.classList.remove('hidden');
    createNoteForm.classList.add('animate-fade-in-up');

    const checklistContainer = document.getElementById('checklist-container');
    const contentInput = document.getElementById('note-content-input');
    const isChecklistInput = document.getElementById('form-is-checklist');

    if (isChecklist) {
        checklistContainer.classList.remove('hidden'); contentInput.classList.add('hidden'); isChecklistInput.value = 'true';
        if (document.getElementById('checklist-items-form').children.length === 0) addChecklistItemInput();
    } else {
        checklistContainer.classList.add('hidden'); contentInput.classList.remove('hidden'); isChecklistInput.value = 'false';
        contentInput.focus();
    }
}

function handleSaveNote() {
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
            if (input.value.trim()) checklistItems.push({ text: input.value.trim(), is_checked: input.dataset.checked === 'true', order: index });
        });
    }
    const labelCheckboxes = createNoteForm.querySelectorAll('input[name="label_ids"]:checked');
    const labelIds = Array.from(labelCheckboxes).map(cb => parseInt(cb.value));

    if (title || content || checklistItems.length > 0) {
        saveNote({ title, content, color, is_pinned: isPinned, is_archived: isArchived, is_checklist: isChecklist, checklist_items: checklistItems, label_ids: labelIds, reminder_date: reminderDate || null });
    }
    resetCreateForm();
}

function handleDiscardNote() { resetCreateForm(); }

function resetCreateForm() {
    createNoteForm.reset();
    createNoteForm.querySelectorAll('input[name="label_ids"]').forEach(cb => cb.checked = false);
    document.getElementById('checklist-items-form').innerHTML = '';
    
    createNoteForm.className = 'hidden bg-white dark:bg-keep-bg-dark border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-4 transition-all duration-300 relative';
    document.getElementById('form-color').value = 'white';
    
    document.querySelector('.icon-pin').classList.remove('fill-1');
    document.getElementById('form-is-pinned').value = 'false';
    document.getElementById('form-reminder-date').value = '';

    createNoteCollapsed.classList.remove('hidden');
}

function togglePinForm(btn) {
    const input = document.getElementById('form-is-pinned');
    const icon = btn.querySelector('.material-symbols-outlined');
    input.value = input.value === 'true' ? 'false' : 'true';
    icon.classList.toggle('fill-1');
}

function toggleArchiveForm(btn) {
    const input = document.getElementById('form-is-archived');
    input.value = input.value === 'true' ? 'false' : 'true';
    btn.classList.toggle('text-gray-900');
}

function setFormColor(color) {
    document.getElementById('form-color').value = color;
    const tailwindClassMap = {
        'white': 'bg-white dark:bg-keep-bg-dark', 'red': 'bg-note-red dark:bg-note-dark-red', 'orange': 'bg-note-orange dark:bg-note-dark-orange',
        'yellow': 'bg-note-yellow dark:bg-note-dark-yellow', 'green': 'bg-note-green dark:bg-note-dark-green', 'teal': 'bg-note-teal dark:bg-note-dark-teal',
        'blue': 'bg-note-blue dark:bg-note-dark-blue', 'darkblue': 'bg-note-darkblue dark:bg-note-dark-darkblue', 'purple': 'bg-note-purple dark:bg-note-dark-purple',
        'pink': 'bg-note-pink dark:bg-note-dark-pink', 'brown': 'bg-note-brown dark:bg-note-dark-brown', 'gray': 'bg-note-gray dark:bg-note-dark-gray'
    };

    createNoteForm.className = 'bg-white dark:bg-keep-bg-dark border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-4 transition-all duration-300 relative animate-fade-in-up';
    if(color !== 'white') {
        createNoteForm.classList.remove('bg-white', 'dark:bg-keep-bg-dark');
        const classes = tailwindClassMap[color].split(' ');
        createNoteForm.classList.add(...classes);
    }
}

function addChecklistItemInput(value = '', isChecked = false, insertAfterNode = null) {
    const container = document.getElementById('checklist-items-form');
    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 group/item animate-fade-in-up';
    div.innerHTML = `
        <span class="material-symbols-outlined text-gray-400 cursor-pointer select-none">${isChecked ? 'check_box' : 'check_box_outline_blank'}</span>
        <input type="text" class="checklist-item-input bg-transparent outline-none flex-1 text-sm text-gray-800 dark:text-gray-200 border-b border-transparent focus:border-gray-300 py-1"
            placeholder="Пункт списка" value="${value}" data-checked="${isChecked}">
        <span class="material-symbols-outlined text-gray-400 cursor-pointer hover:text-red-500 opacity-0 group-hover/item:opacity-100 transition-all" onclick="this.parentElement.remove()">close</span>
    `;
    if (insertAfterNode && insertAfterNode.parentNode === container) {
        if (insertAfterNode.nextSibling) container.insertBefore(div, insertAfterNode.nextSibling);
        else container.appendChild(div);
    } else container.appendChild(div);
    div.querySelector('input').focus();
}

function handleChecklistKeydown(event, input) {
    if (event.key === 'Enter') {
        event.preventDefault(); addChecklistItemInput('', false, input.parentElement);
    } else if (event.key === 'Backspace' && input.value === '' && document.getElementById('checklist-items-form').children.length > 1) {
        event.preventDefault();
        const prev = input.parentElement.previousElementSibling;
        input.parentElement.remove();
        if (prev) {
            const prevInput = prev.querySelector('input'); prevInput.focus();
            const len = prevInput.value.length; prevInput.setSelectionRange(len, len);
        }
    }
}

async function saveNote(data) {
    try {
        const res = await fetch('/api/v1/notes/', {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, body: JSON.stringify(data)
        });
        if (res.ok) {
            const note = await res.json(); prependNoteToGrid(note);
        }
    } catch (e) { console.error(e); }
}

function prependNoteToGrid(note) {
    const noteNode = createNoteCardHTML(note);
    if (note.is_pinned) pinnedGrid.prepend(noteNode);
    else otherGrid.prepend(noteNode);
    updateSectionTitles();
}

function createNoteCardHTML(note) {
    const el = (tag, classes = '') => {
        const e = document.createElement(tag);
        if(classes) e.className = classes;
        return e;
    };

    const colorClassMap = {
        'white': 'bg-white dark:bg-keep-bg-dark', 'red': 'bg-note-red dark:bg-note-dark-red', 'orange': 'bg-note-orange dark:bg-note-dark-orange',
        'yellow': 'bg-note-yellow dark:bg-note-dark-yellow', 'green': 'bg-note-green dark:bg-note-dark-green', 'teal': 'bg-note-teal dark:bg-note-dark-teal',
        'blue': 'bg-note-blue dark:bg-note-dark-blue', 'darkblue': 'bg-note-darkblue dark:bg-note-dark-darkblue', 'purple': 'bg-note-purple dark:bg-note-dark-purple',
        'pink': 'bg-note-pink dark:bg-note-dark-pink', 'brown': 'bg-note-brown dark:bg-note-dark-brown', 'gray': 'bg-note-gray dark:bg-note-dark-gray'
    };
    const bgClass = colorClassMap[note.color] || colorClassMap['white'];

    const card = el('div', `note-card animate-fade-in-up relative group rounded-xl border border-gray-200 dark:border-gray-700 p-4 transition-all duration-300 hover:shadow-lg cursor-default flex flex-col justify-between ${bgClass}`);
    card.dataset.id = note.id;
    card.dataset.pinned = note.is_pinned;
    if (note.reminder_date) card.dataset.reminder = note.reminder_date;

    const pinContainer = el('div', `absolute top-2 right-2 opacity-0 group-hover:opacity-100 ${note.is_pinned ? 'opacity-100' : ''} transition-opacity duration-200 z-10`);
    const pinBtn = el('button', 'p-1 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-gray-700 dark:text-gray-300 transition-colors');
    pinBtn.onclick = (e) => { e.stopPropagation(); togglePinNote(note.id); };
    const pinIcon = el('span', `material-symbols-outlined text-[20px] ${note.is_pinned ? 'fill-1' : ''}`);
    pinIcon.textContent = 'keep';
    pinBtn.appendChild(pinIcon); pinContainer.appendChild(pinBtn); card.appendChild(pinContainer);

    const contentDiv = el('div', 'cursor-pointer flex-1');
    contentDiv.onclick = () => openEditModal(note.id);

    if (note.title) {
        const h3 = el('h3', 'font-medium text-lg mb-2 text-gray-900 dark:text-gray-100 break-words pr-6');
        h3.textContent = note.title; contentDiv.appendChild(h3);
    }

    if (note.is_checklist) {
        const ul = el('ul', 'space-y-1');
        note.checklist_items.slice(0, 5).forEach(item => {
            const li = el('li', 'flex items-start gap-2 text-sm text-gray-800 dark:text-gray-200');
            const spanIcon = el('span', 'material-symbols-outlined text-[18px] text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-pointer transition-colors');
            spanIcon.onclick = (e) => { e.stopPropagation(); toggleCheckbox(item.id, spanIcon); };
            spanIcon.textContent = item.is_checked ? 'check_box' : 'check_box_outline_blank';
            const spanText = el('span', `transition-all duration-200 break-all ${item.is_checked ? 'line-through text-gray-500' : ''}`);
            spanText.textContent = item.text;
            li.appendChild(spanIcon); li.appendChild(spanText); ul.appendChild(li);
        });
        if (note.checklist_items.length > 5) {
            const liMore = el('li', 'text-xs text-gray-500 pl-7 font-medium');
            liMore.textContent = `+ еще ${note.checklist_items.length - 5}`;
            ul.appendChild(liMore);
        }
        contentDiv.appendChild(ul);
    } else {
        const p = el('p', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden');
        p.textContent = note.content.substring(0, 300); contentDiv.appendChild(p);
    }

    if (note.reminder_date) {
         const div = el('div', 'mt-3');
         const badge = el('span', 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-black/5 dark:bg-white/10 text-gray-800 dark:text-gray-200');
         const icon = el('span', 'material-symbols-outlined text-[14px] mr-1'); icon.textContent = 'schedule';
         badge.appendChild(icon); badge.appendChild(document.createTextNode(" " + (note.formatted_reminder_date || note.reminder_date)));
         div.appendChild(badge); contentDiv.appendChild(div);
    }

    if (note.labels && note.labels.length > 0) {
        const labelsDiv = el('div', 'flex flex-wrap gap-1 mt-3');
        note.labels.forEach(l => {
            const span = el('span', 'px-2 py-1 rounded-full bg-black/5 dark:bg-white/10 text-xs font-medium text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-black/10 dark:hover:bg-white/20 transition-colors');
            span.onclick = (e) => { e.stopPropagation(); window.location.href=`/label/${encodeURIComponent(l.name)}/`; };
            span.textContent = l.name; labelsDiv.appendChild(span);
        });
        contentDiv.appendChild(labelsDiv);
    }

    card.appendChild(contentDiv);

    const actionsDiv = el('div', 'flex justify-between items-center mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 h-8');
    const btnGroup = el('div', 'flex gap-1');

    const createActionBtn = (iconName, title, onClick) => {
        const btn = el('button', 'p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 text-gray-600 dark:text-gray-300 transition-colors');
        btn.title = title; btn.onclick = (e) => { e.stopPropagation(); onClick(note.id); };
        const icon = el('span', 'material-symbols-outlined text-[18px]'); icon.textContent = iconName;
        btn.appendChild(icon); return btn;
    };

    if (note.is_trashed) {
        btnGroup.appendChild(createActionBtn('delete_forever', 'Удалить навсегда', deleteNoteForever));
        btnGroup.appendChild(createActionBtn('restore_from_trash', 'Восстановить', trashNote));
    } else {
        if (note.is_archived) btnGroup.appendChild(createActionBtn('unarchive', 'Разархивировать', archiveNote));
        else btnGroup.appendChild(createActionBtn('archive', 'В архив', archiveNote));
        btnGroup.appendChild(createActionBtn('delete', 'Удалить', trashNote));
    }

    actionsDiv.appendChild(btnGroup); card.appendChild(actionsDiv);
    return card;
}

async function performOptimisticRemove(id, apiPromise) {
    const card = document.querySelector(`.note-card[data-id="${id}"]`);
    if(!card) return;
    const parent = card.parentNode;
    const nextSibling = card.nextSibling;
    
    card.style.transform = 'scale(0.9)';
    card.style.opacity = '0';
    setTimeout(() => { card.remove(); updateSectionTitles(); }, 200);

    try {
        const res = await apiPromise();
        if (!res.ok && res.status !== 404) throw new Error(`Failed`);
    } catch (e) {
        console.error(e);
        card.style.transform = 'scale(1)'; card.style.opacity = '1';
        if (nextSibling) parent.insertBefore(card, nextSibling);
        else parent.appendChild(card);
        showToast("Ошибка действия");
    }
}

function archiveNote(id) { performOptimisticRemove(id, () => fetch(`/api/v1/notes/${id}/archive/`, { method: 'POST', headers: {'X-CSRFToken': csrftoken} })); }
function trashNote(id) { performOptimisticRemove(id, () => fetch(`/api/v1/notes/${id}/trash/`, { method: 'POST', headers: {'X-CSRFToken': csrftoken} })); }
function deleteNoteForever(id) { performOptimisticRemove(id, () => fetch(`/api/v1/notes/${id}/`, { method: 'DELETE', headers: {'X-CSRFToken': csrftoken} })); }

async function togglePinNote(id) {
    const card = document.querySelector(`.note-card[data-id="${id}"]`);
    if(!card) return;
    const wasPinned = card.dataset.pinned === 'true';
    const newPinned = !wasPinned;

    updateCardPinVisuals(card, newPinned);
    if (newPinned) pinnedGrid.prepend(card);
    else otherGrid.prepend(card);
    updateSectionTitles();

    try {
        const res = await fetch(`/api/v1/notes/${id}/pin/`, { method: 'POST', headers: {'X-CSRFToken': csrftoken} });
        if(!res.ok) throw new Error('Failed');
    } catch (e) {
        updateCardPinVisuals(card, wasPinned);
        if (wasPinned) pinnedGrid.prepend(card); else otherGrid.prepend(card);
        updateSectionTitles(); showToast("Не удалось закрепить");
    }
}

async function toggleCheckbox(itemId, span) {
    const isChecked = span.textContent.trim() === 'check_box';
    const newStatus = !isChecked;
    span.textContent = newStatus ? 'check_box' : 'check_box_outline_blank';
    const textSpan = span.nextElementSibling;
    if(newStatus) textSpan.classList.add('line-through', 'text-gray-500');
    else textSpan.classList.remove('line-through', 'text-gray-500');

    await fetch(`/api/v1/checklist-items/${itemId}/`, {
        method: 'PATCH', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken}, body: JSON.stringify({is_checked: newStatus})
    });
}

let searchTimeout;
if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => { loadNotes(e.target.value); }, 300);
    });
}

async function loadNotes(urlOrQuery) {
    let url;
    if (urlOrQuery && (urlOrQuery.startsWith('/') || urlOrQuery.startsWith('http'))) url = urlOrQuery;
    else url = urlOrQuery ? `/api/v1/notes/?search=${encodeURIComponent(urlOrQuery)}` : '/api/v1/notes/';

    const separator = url.includes('?') ? '&' : '?';
    if (window.activeTab === 'archive') url += `${separator}is_archived=true`;
    else if (window.activeTab === 'trash') url += `${separator}is_trashed=true`;
    else if (window.activeTab === 'notes') url += `${separator}is_archived=false&is_trashed=false`;
    else if (window.activeTab === 'label' && window.activeLabel && window.userLabels) {
        const labelObj = window.userLabels.find(l => l.name === window.activeLabel);
        if (labelObj) url += `${separator}labels=${labelObj.id}&is_archived=false&is_trashed=false`;
    }

    try {
        const res = await fetch(url);
        const data = await res.json();
        pinnedGrid.innerHTML = ''; otherGrid.innerHTML = '';
        const notes = data.results || data;

        if (notes.length === 0 && url.includes('search=')) {
                otherGrid.innerHTML = '<div class="col-span-full text-center text-gray-500 py-10 animate-fade-in-up">Ничего не найдено</div>';
        } else {
            [...notes].reverse().forEach(note => prependNoteToGrid(note));
        }
        updateSectionTitles(); renderPagination(data);
    } catch (e) { console.error("Failed to load notes", e); }
}

function renderPagination(data) {
    const container = document.getElementById('pagination-container');
    if (!container) return;
    if (!data.next && !data.previous) { container.innerHTML = ''; return; }

    let currentPage = 1;
    if (data.next) { const match = data.next.match(/page=(\d+)/); currentPage = match ? parseInt(match[1]) - 1 : 1; } 
    else if (data.previous) { const match = data.previous.match(/page=(\d+)/); currentPage = match ? parseInt(match[1]) + 1 : 2; }

    const totalPages = Math.ceil(data.count / 12);
    if (totalPages <= 1) { container.innerHTML = ''; return; }

    const createBtn = (isNext, url, disabled) => {
        if (disabled) {
            const span = document.createElement('span'); span.className = "p-2 text-gray-400 dark:text-gray-600 cursor-not-allowed";
            span.innerHTML = `<span class="material-symbols-outlined text-xl">${isNext ? 'chevron_right' : 'chevron_left'}</span>`;
            return span;
        } else {
            const a = document.createElement('a'); a.href = url;
            a.className = "p-2 rounded-lg hover:bg-white/50 dark:hover:bg-white/10 text-gray-700 dark:text-gray-200 transition-colors";
            a.innerHTML = `<span class="material-symbols-outlined text-xl">${isNext ? 'chevron_right' : 'chevron_left'}</span>`;
            a.onclick = (e) => { e.preventDefault(); loadNotes(url); };
            return a;
        }
    };

    container.innerHTML = '';
    const wrapper = document.createElement('div'); wrapper.className = "flex justify-center mt-8 pb-4 animate-fade-in-up";
    const nav = document.createElement('nav'); nav.className = "inline-flex items-center p-1 rounded-xl bg-white/30 dark:bg-black/30 backdrop-blur-md border border-white/20 dark:border-white/10 shadow-lg";
    nav.appendChild(createBtn(false, data.previous, !data.previous));
    const pageInfo = document.createElement('span'); pageInfo.className = "px-4 py-2 text-sm font-medium text-gray-800 dark:text-gray-200";
    pageInfo.textContent = `Страница ${currentPage} из ${totalPages}`;
    nav.appendChild(pageInfo);
    nav.appendChild(createBtn(true, data.next, !data.next));
    wrapper.appendChild(nav); container.appendChild(wrapper);
}

async function openEditModal(id) {
    const res = await fetch(`/api/v1/notes/${id}/`);
    const note = await res.json();
    const modal = document.getElementById('edit-modal');
    const content = document.getElementById('edit-modal-content');
    content.innerHTML = '';
    
    const el = (tag, classes = '', props = {}) => {
        const e = document.createElement(tag);
        if(classes) e.className = classes;
        for(const [k, v] of Object.entries(props)) {
            if(k === 'dataset') { for(const [dk, dv] of Object.entries(v)) e.dataset[dk] = dv; } 
            else { e[k] = v; }
        }
        return e;
    };

    const header = el('div', 'flex justify-between items-start mb-2');
    const titleInput = el('input', 'w-full bg-transparent outline-none text-xl font-medium placeholder-gray-500 text-gray-800 dark:text-gray-200', { type: 'text', placeholder: 'Заголовок', id: 'edit-title', value: note.title });
    const pinBtn = el('button', 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 p-1 rounded-full transition-colors', {type: 'button'});
    pinBtn.onclick = () => toggleEditPin(pinBtn);
    const pinIcon = el('span', `material-symbols-outlined icon-pin ${note.is_pinned ? 'fill-1' : ''}`); pinIcon.textContent = 'keep'; pinBtn.appendChild(pinIcon);
    const isPinnedInput = el('input', '', {type: 'hidden', id: 'edit-is-pinned', value: note.is_pinned});
    header.append(titleInput, pinBtn, isPinnedInput); content.append(header);

    if (note.is_checklist) {
        const checklistContainer = el('div', 'space-y-2 mb-2', {id: 'edit-checklist-container'});
        const itemsContainer = el('div', '', {id: 'edit-checklist-items-form'});
        note.checklist_items.sort((a,b) => a.order - b.order).forEach(item => { itemsContainer.appendChild(createChecklistItemElement(item.text, item.is_checked, item.id)); });
        const addBtn = el('div', 'flex items-center gap-2 text-gray-500 cursor-pointer p-1 hover:bg-black/5 dark:hover:bg-white/5 rounded transition-colors');
        addBtn.onclick = () => addChecklistItemInputEdit();
        addBtn.innerHTML = '<span class="material-symbols-outlined text-sm">add</span><span class="text-sm">Пункт списка</span>';
        checklistContainer.append(itemsContainer, addBtn); content.append(checklistContainer);
        content.append(el('textarea', 'hidden', {id: 'edit-content'}));
    } else {
        const textarea = el('textarea', 'w-full bg-transparent outline-none resize-none overflow-hidden placeholder-gray-500 text-sm text-gray-800 dark:text-gray-200 min-h-[150px]', { id: 'edit-content', placeholder: 'Заметка', value: note.content });
        content.append(textarea);
    }

    const footer = el('div', 'flex justify-between items-center mt-4');
    const actionsLeft = el('div', 'flex gap-1 text-gray-600 dark:text-gray-400 items-center');

    const colorWrapper = el('div', 'relative');
    const colorBtn = el('button', 'p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors', {type: 'button', title: 'Цвет'});
    colorBtn.onclick = (e) => { e.stopPropagation(); toggleMenu(colorBtn); };
    colorBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">palette</span>';
    const colorMenu = el('div', 'absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg p-2 flex gap-1 hidden menu-dropdown border dark:border-gray-700 z-20 flex-wrap w-48 transition-all');
    colorMenu.onclick = (e) => e.stopPropagation();
    ['white','red','orange','yellow','green','teal','blue','darkblue','purple','pink','brown','gray'].forEach(c => {
        const circle = el('div', `w-6 h-6 rounded-full border border-gray-300 dark:border-gray-600 cursor-pointer ${getColorClass(c)}`);
        circle.onclick = () => setEditColor(c); colorMenu.appendChild(circle);
    });
    colorWrapper.append(colorBtn, colorMenu); actionsLeft.append(colorWrapper);

    content.append(el('input', '', {type: 'hidden', id: 'edit-color', value: note.color}));
    content.append(el('input', '', {type: 'hidden', id: 'edit-is-archived', value: note.is_archived}));
    content.append(el('input', '', {type: 'hidden', id: 'edit-is-checklist', value: note.is_checklist}));

    const archiveBtn = el('button', `p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors ${note.is_archived ? 'text-gray-900 bg-gray-200 dark:bg-gray-600' : ''}`, {type: 'button'});
    archiveBtn.onclick = () => toggleEditArchive(archiveBtn);
    archiveBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">archive</span>';

    const reminderWrapper = el('div', 'relative');
    const reminderBtn = el('button', 'p-2 rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors', {type: 'button', title: 'Напомнить'});
    reminderBtn.onclick = (e) => { e.stopPropagation(); toggleMenu(reminderBtn); };
    reminderBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">notifications</span>';

    const reminderMenu = el('div', 'absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg p-2 hidden menu-dropdown border dark:border-gray-700 z-20 w-64');
    reminderMenu.onclick = (e) => e.stopPropagation();

    const reminderInput = el('input', 'w-full bg-gray-100 dark:bg-gray-700 border-none rounded p-2 text-sm text-gray-800 dark:text-gray-200 outline-none', {type: 'datetime-local', id: 'edit-reminder-date'});
    if (note.reminder_date) {
        // Формат datetime-local ожидает YYYY-MM-DDTHH:MM, а из API может приходить полная ISO-дата
        reminderInput.value = note.reminder_date.substring(0, 16);
    }
    reminderMenu.appendChild(reminderInput);
    reminderWrapper.append(reminderBtn, reminderMenu);
    actionsLeft.append(reminderWrapper);

    actionsLeft.append(archiveBtn);
    footer.append(actionsLeft);

    const doneBtn = el('button', 'px-4 py-2 hover:bg-black/5 dark:hover:bg-white/10 rounded-lg text-gray-800 dark:text-gray-200 font-medium transition-colors', {type: 'button'});
    doneBtn.textContent = 'Закрыть';
    doneBtn.onclick = () => saveEditedNote(id);
    footer.append(doneBtn); content.append(footer);

    setEditColor(note.color);
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.classList.remove('opacity-0');
        content.classList.remove('scale-95');
        content.classList.add('scale-100');
    }, 10);
}

function closeEditModal(e) {
    if(e && e.target && e.target.id === 'edit-modal') {
        const modal = document.getElementById('edit-modal');
        const content = document.getElementById('edit-modal-content');
        modal.classList.add('opacity-0');
        content.classList.remove('scale-100');
        content.classList.add('scale-95');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }
}

function setEditColor(color) {
    document.getElementById('edit-color').value = color;
    const form = document.getElementById('edit-modal-content');
    const tailwindClassMap = {
        'white': 'bg-white dark:bg-keep-bg-dark', 'red': 'bg-note-red dark:bg-note-dark-red', 'orange': 'bg-note-orange dark:bg-note-dark-orange',
        'yellow': 'bg-note-yellow dark:bg-note-dark-yellow', 'green': 'bg-note-green dark:bg-note-dark-green', 'teal': 'bg-note-teal dark:bg-note-dark-teal',
        'blue': 'bg-note-blue dark:bg-note-dark-blue', 'darkblue': 'bg-note-darkblue dark:bg-note-dark-darkblue', 'purple': 'bg-note-purple dark:bg-note-dark-purple',
        'pink': 'bg-note-pink dark:bg-note-dark-pink', 'brown': 'bg-note-brown dark:bg-note-dark-brown', 'gray': 'bg-note-gray dark:bg-note-dark-gray'
    };
    form.className = 'rounded-xl shadow-2xl w-full max-w-2xl p-6 relative mx-4 transition-all duration-300 transform scale-100';
    if(color !== 'white') {
        const classes = tailwindClassMap[color].split(' ');
        form.classList.add(...classes);
    } else {
        form.classList.add('bg-white', 'dark:bg-keep-bg-dark');
    }
}

function getColorClass(c) {
    const map = {
        'white': 'bg-white', 'red': 'bg-note-red', 'orange': 'bg-note-orange', 'yellow': 'bg-note-yellow', 'green': 'bg-note-green', 
        'teal': 'bg-note-teal', 'blue': 'bg-note-blue', 'darkblue': 'bg-note-darkblue', 'purple': 'bg-note-purple', 'pink': 'bg-note-pink', 
        'brown': 'bg-note-brown', 'gray': 'bg-note-gray'
    };
    return map[c];
}

async function saveEditedNote(id) {
    const title = document.getElementById('edit-title').value;
    const content = document.getElementById('edit-content') ? document.getElementById('edit-content').value : '';
    const isPinned = document.getElementById('edit-is-pinned').value === 'true';
    const isArchived = document.getElementById('edit-is-archived').value === 'true';
    const isChecklist = document.getElementById('edit-is-checklist').value === 'true';
    const color = document.getElementById('edit-color').value;
    const reminderDateInput = document.getElementById('edit-reminder-date');
    const reminderDate = reminderDateInput ? reminderDateInput.value : null;

    let checklistItems = [];
    if (isChecklist) {
        document.querySelectorAll('#edit-checklist-items-form .edit-checklist-item-input').forEach((input, index) => {
            if(input.value.trim()) checklistItems.push({ text: input.value.trim(), is_checked: input.dataset.checked === 'true', order: index, id: input.dataset.id ? parseInt(input.dataset.id) : undefined });
        });
    }

    await fetch(`/api/v1/notes/${id}/`, {
        method: 'PATCH', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
        body: JSON.stringify({ title, content, is_pinned: isPinned, is_archived: isArchived, color, checklist_items: isChecklist ? checklistItems : undefined, reminder_date: reminderDate || null })
    });

    closeEditModal({target: document.getElementById('edit-modal')});
    loadNotes(globalSearch ? globalSearch.value : '');
}

function createChecklistItemElement(text, isChecked, id=null) {
    const div = document.createElement('div'); div.className = 'flex items-center gap-2 group/item';
    div.innerHTML = `<span class="material-symbols-outlined text-gray-400 cursor-pointer select-none">${isChecked ? 'check_box' : 'check_box_outline_blank'}</span><input type="text" class="edit-checklist-item-input bg-transparent outline-none flex-1 text-sm text-gray-800 dark:text-gray-200 border-b border-transparent focus:border-blue-500 transition-colors py-1" placeholder="Пункт списка" value=""><span class="material-symbols-outlined text-gray-400 cursor-pointer hover:text-red-500 opacity-0 group-hover/item:opacity-100 transition-all">close</span>`;
    const input = div.querySelector('input'); input.value = text;
    if(id) input.dataset.id = id; input.dataset.checked = isChecked; return div;
}

function showToast(message) {
    const div = document.createElement('div');
    div.className = 'fixed bottom-4 right-4 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-xl z-50 transition-all duration-300 flex items-center gap-2 transform translate-y-10 opacity-0';
    div.innerHTML = `<span class="material-symbols-outlined text-yellow-400">notifications_active</span><span>${message}</span>`;
    document.body.appendChild(div);
    
    setTimeout(() => { div.classList.remove('translate-y-10', 'opacity-0'); }, 10);
    setTimeout(() => { 
        div.classList.add('opacity-0', 'translate-y-2'); 
        setTimeout(() => div.remove(), 300); 
    }, 4000);
}

function toggleEditArchive(btn) {
    const input = document.getElementById('edit-is-archived');
    input.value = input.value === 'true' ? 'false' : 'true';
    btn.classList.toggle('text-gray-900'); btn.classList.toggle('bg-gray-200'); btn.classList.toggle('dark:bg-gray-600');
}

function toggleEditPin(btn) {
    const input = document.getElementById('edit-is-pinned');
    const icon = btn.querySelector('.material-symbols-outlined');
    input.value = input.value === 'true' ? 'false' : 'true';
    icon.classList.toggle('fill-1');
}

// --- ЛОГИКА ДЛЯ ЯРЛЫКОВ (ТЕГОВ) ---
function openLabelModal() {
    const m = document.getElementById('label-modal');
    const c = document.getElementById('label-modal-content');
    m.classList.remove('hidden');
    setTimeout(() => { m.classList.remove('opacity-0'); c.classList.remove('scale-95'); c.classList.add('scale-100'); }, 10);
}

function closeLabelModal(e) {
    if (e && e.target && e.target.id !== 'label-modal' && e.type === 'click') return;
    const m = document.getElementById('label-modal');
    const c = document.getElementById('label-modal-content');
    m.classList.add('opacity-0'); c.classList.remove('scale-100'); c.classList.add('scale-95');
    setTimeout(() => { m.classList.add('hidden'); }, 300);
}

function handleLabelModalDone() {
    closeLabelModal();
    location.reload(); // Перезагружаем страницу, чтобы обновить боковое меню
}

async function createLabel() {
    const input = document.getElementById('new-label-input');
    const name = input.value.trim();
    if (!name) return;
    try {
        const res = await fetch('/api/v1/labels/', {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, body: JSON.stringify({name})
        });
        if (res.ok) {
            input.value = '';
            location.reload(); 
        } else {
            const data = await res.json();
            if (data.name) showToast(data.name[0]);
        }
    } catch(e) { console.error(e); }
}

async function deleteLabel(id, btn) {
    try {
        const res = await fetch(`/api/v1/labels/${id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrftoken } });
        if (res.ok) {
            btn.closest('.group').remove();
        }
    } catch(e) { console.error(e); }
}

function enableLabelRename(id, span) {
    const oldName = span.textContent;
    const input = document.createElement('input');
    input.type = 'text'; input.value = oldName; 
    input.className = 'flex-1 bg-transparent outline-none text-gray-800 dark:text-gray-200 text-sm font-medium border-b border-yellow-500';
    span.replaceWith(input);
    input.focus();
    
    const save = async () => {
        const newName = input.value.trim();
        if (newName && newName !== oldName) {
            await fetch(`/api/v1/labels/${id}/`, {
                method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken }, body: JSON.stringify({name: newName})
            });
        }
        const newSpan = document.createElement('span');
        newSpan.className = 'flex-1 text-gray-800 dark:text-gray-200 text-sm font-medium cursor-text';
        newSpan.textContent = newName || oldName;
        newSpan.onclick = () => enableLabelRename(id, newSpan);
        input.replaceWith(newSpan);
    };
    
    input.onblur = save;
    input.onkeydown = (e) => { if (e.key === 'Enter') input.blur(); };
}
