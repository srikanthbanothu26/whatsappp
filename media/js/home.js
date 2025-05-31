document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chatBox');
    const contactList = document.getElementById('contactList');
    const searchInput = document.getElementById('searchInput');
    const messageInput = document.querySelector('input[type="text"]');
    const sendButton = document.querySelector('button');

    let selectedContact = null;
    let lastMessageId = 0;
    let pollingInterval = null;

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    function appendMessages(messages) {
        messages.forEach(msg => {
            const div = document.createElement('div');
            const isCurrentUser = msg.is_current_user;

            div.className = `max-w-xs px-4 py-2 rounded-lg shadow text-sm ${
                isCurrentUser ? 'bg-blue-500 text-white self-end ml-auto' : 'bg-gray-200 text-gray-800'
            }`;

            div.innerHTML = `
                <p>${escapeHtml(msg.message)}</p>
                <span class="text-xs block mt-1 ${isCurrentUser ? 'text-blue-200' : 'text-gray-600'}">${msg.date_time}</span>
            `;

            const wrapper = document.createElement('div');
            wrapper.className = `flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-1`;
            wrapper.appendChild(div);
            chatBox.appendChild(wrapper);

            // Update lastMessageId
            if (msg.id > lastMessageId) {
                lastMessageId = msg.id;
            }
        });

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function loadMessages(contactUsername, fullReload = true) {
        if (!contactUsername) return;

        let url = `/get_messages/?contact=${encodeURIComponent(contactUsername)}`;
        if (!fullReload && lastMessageId) {
            url += `&last_id=${lastMessageId}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(messages => {
                if (fullReload) {
                    chatBox.innerHTML = '';
                }

                if (messages.length === 0 && fullReload) {
                    chatBox.innerHTML = '<p class="text-center text-gray-500 mt-4">No messages yet.</p>';
                    return;
                }

                appendMessages(messages);
            })
            .catch(err => {
                console.error('Failed to load messages:', err);
            });
    }

   function sendMessage() {
    const messageText = messageInput.value.trim();
    if (!messageText || !selectedContact) return;

    fetch('/send_message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            contact: selectedContact,
            message: messageText
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            messageInput.value = '';
            // Update lastMessageId to the new message's ID
            if (data.message_id && data.message_id > lastMessageId) {
                lastMessageId = data.message_id;
            }
            // Instead of full reload, just fetch new messages after lastMessageId
            loadMessages(selectedContact, false);
        } else {
            alert(data.error || 'Failed to send message');
        }
    })
    .catch(err => {
        console.error('Send message error:', err);
    });
}


    function startPolling() {
        if (pollingInterval) clearInterval(pollingInterval);
        pollingInterval = setInterval(() => {
            if (selectedContact) {
                loadMessages(selectedContact, false); // only new
            }
        }, 3000); // every 3 seconds
    }

    function setupContactClickEvents() {
    document.querySelectorAll('.contact-item').forEach(item => {
        item.addEventListener('click', function () {
            const contactName = this.dataset.name;

            if (selectedContact === contactName) return; // avoid reloading same contact

            selectedContact = contactName;
            lastMessageId = 0;
            chatBox.innerHTML = '';
            loadMessages(contactName, true);
            startPolling();

            // UI feedback
            document.querySelectorAll('.contact-item').forEach(i => i.classList.remove('bg-blue-100'));
            this.classList.add('bg-blue-100');
        });
    });
}


    // Initial setup
    setupContactClickEvents();

    searchInput.addEventListener('input', async () => {
        const query = searchInput.value.trim();
        try {
            const response = await fetch(`/search_contacts/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            contactList.innerHTML = '';
            if (data.length === 0) {
                contactList.innerHTML = '<p class="text-center text-gray-500">No contacts found.</p>';
                return;
            }

            data.forEach(contact => {
                const div = document.createElement('div');
                div.className = 'contact-item bg-white hover:bg-gray-50 transition-all p-4 rounded shadow-sm border border-gray-200 cursor-pointer';
                div.textContent = contact.name;
                div.dataset.name = contact.name;
                contactList.appendChild(div);
            });
            setupContactClickEvents();
        } catch (error) {
            console.error('Search error:', error);
        }
    });

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
});
