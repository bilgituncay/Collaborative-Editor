(function () {
    const documentId = window.EDITOR_CONFIG.documentId;
    const documentLanguage = window.EDITOR_CONFIG.documentLanguage;
    const canEdit = window.EDITOR_CONFIG.canEdit;
    
    // Initialize CodeMirror
    const editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: documentLanguage,
        theme: 'monokai',
        lineNumbers: true,
        lineWrapping: false,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        matchBrackets: true,
        autoCloseBrackets: true,
        styleActiveLine: true,
        viewportMargin: Infinity,
        readOnly: !canEdit
    });

    // State management
    let socket = null;
    let userId = null;
    let isLocalChange = false;
    let connectedUsers = new Map();
    let remoteCursors = new Map();
    
    const userColors = [
        '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
        '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
    ];

    // WebSocket connection
    function connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/editor/${documentId}/`;
        
        socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
            updateConnectionStatus(true);
            console.log('WebSocket connected');
        };
        
        socket.onclose = () => {
            updateConnectionStatus(false);
            console.log('WebSocket disconnected');
            setTimeout(connect, 3000);
        };
        
        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleMessage(data);
        };
    }

    function handleMessage(data) {
        switch(data.type) {
            case 'document_content':
                userId = data.user_id;
                isLocalChange = true;
                editor.setValue(data.content);
                isLocalChange = false;
                break;
                
            case 'text_change':
                if (data.user_id !== userId) {
                    applyRemoteChange(data);
                }
                break;
                
            case 'cursor_position':
                updateRemoteCursor(data.user_id, data.position, data.selection);
                break;
                
            case 'user_joined':
                addUser(data.user_id);
                break;
                
            case 'user_left':
                removeUser(data.user_id);
                break;
        }
    }

    function applyRemoteChange(data) {
        isLocalChange = true;
        const doc = editor.getDoc();
        
        switch(data.operation) {
            case 'insert':
                const pos = doc.posFromIndex(data.position);
                doc.replaceRange(data.text, pos);
                break;
                
            case 'delete':
                const from = doc.posFromIndex(data.position);
                const to = doc.posFromIndex(data.position + data.length);
                doc.replaceRange('', from, to);
                break;
                
            case 'replace':
                editor.setValue(data.content);
                break;
        }
        
        isLocalChange = false;
    }

    editor.on('change', (instance, changeObj) => {
        if (isLocalChange || !socket || socket.readyState !== WebSocket.OPEN) return;
        
        const doc = instance.getDoc();
        const from = doc.indexFromPos(changeObj.from);
        const content = instance.getValue();
        
        let operation, text, length;
        
        if (changeObj.origin === '+input' || changeObj.origin === 'paste') {
            operation = 'insert';
            text = changeObj.text.join('\n');
        } else if (changeObj.origin === '+delete' || changeObj.origin === 'cut') {
            operation = 'delete';
            text = '';
            length = changeObj.removed.join('\n').length;
        } else {
            operation = 'replace';
            text = changeObj.text.join('\n');
        }
        
        socket.send(JSON.stringify({
            type: 'text_change',
            operation: operation,
            position: from,
            text: text,
            length: length,
            content: content
        }));
    });

    editor.on('cursorActivity', () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) return;
        
        const doc = editor.getDoc();
        const cursor = doc.getCursor();
        const position = doc.indexFromPos(cursor);
        
        let selection = null;
        if (doc.somethingSelected()) {
            const from = doc.indexFromPos(doc.getCursor('from'));
            const to = doc.indexFromPos(doc.getCursor('to'));
            selection = { from, to };
        }
        
        socket.send(JSON.stringify({
            type: 'cursor_position',
            position: position,
            selection: selection
        }));
    });

    function addUser(uid) {
        if (!connectedUsers.has(uid)) {
            const color = userColors[connectedUsers.size % userColors.length];
            connectedUsers.set(uid, { color });
            updateUsersList();
        }
    }

    function removeUser(uid) {
        connectedUsers.delete(uid);
        remoteCursors.delete(uid);
        updateUsersList();
        removeRemoteCursor(uid);
    }

    function updateUsersList() {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '';
        
        connectedUsers.forEach((user, uid) => {
            const badge = document.createElement('div');
            badge.className = 'user-badge';
            badge.style.background = user.color + '33';
            badge.style.color = user.color;
            badge.textContent = `User ${uid.toString().substring(0, 4)}`;
            usersList.appendChild(badge);
        });
    }

    function updateRemoteCursor(uid, position, selection) {
        const doc = editor.getDoc();
        const pos = doc.posFromIndex(position);
        const coords = editor.cursorCoords(pos, 'local');
        
        let cursorEl = remoteCursors.get(uid);
        if (!cursorEl) {
            cursorEl = document.createElement('div');
            cursorEl.className = 'remote-cursor';
            cursorEl.dataset.user = `User ${uid.toString().substring(0, 4)}`;
            editor.getWrapperElement().appendChild(cursorEl);
            remoteCursors.set(uid, cursorEl);
        }
        
        const user = connectedUsers.get(uid);
        if (user) {
            cursorEl.style.background = user.color;
            cursorEl.style.left = coords.left + 'px';
            cursorEl.style.top = coords.top + 'px';
        }
    }

    function removeRemoteCursor(uid) {
        const cursorEl = remoteCursors.get(uid);
        if (cursorEl) {
            cursorEl.remove();
            remoteCursors.delete(uid);
        }
    }

    function updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        status.className = 'connection-status ' + (connected ? 'connected' : 'disconnected');
        status.textContent = connected ? 'Connected' : 'Disconnected';
    }

    connect();

})();