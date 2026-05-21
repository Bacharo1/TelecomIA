
document.addEventListener('DOMContentLoaded', function() {
    const btnLogin = document.getElementById('btnLogin');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMsg = document.getElementById('errorMsg');

    // On n'exécute ce code que si on est bien sur la page de connexion
    if (!btnLogin || !usernameInput || !passwordInput) return;

    function afficherErreur(message) {
        errorMsg.textContent = message;
        errorMsg.classList.add('visible');
        btnLogin.disabled = false;
        btnLogin.textContent = 'Se connecter';
    }

    btnLogin.addEventListener('click', async function(e) {
        e.preventDefault();
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            afficherErreur('Veuillez remplir tous les champs.');
            return;
        }

        btnLogin.disabled = true;
        btnLogin.textContent = 'Connexion en cours…';
        errorMsg.classList.remove('visible');

        try {
            const response = await fetch('http://localhost:8001/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                sessionStorage.setItem('loggedIn', 'true');
                sessionStorage.setItem('username', data.username);
                if (data.equipe_id) sessionStorage.setItem('equipe_id', data.equipe_id);
                window.location.href = 'index.html';
            } else if (response.status === 401) {
                afficherErreur('Identifiant ou mot de passe incorrect.');
            } else {
                const errData = await response.json().catch(() => ({}));
                afficherErreur(errData.detail || 'Erreur serveur.');
            }
        } catch (error) {
            afficherErreur('Impossible de contacter le serveur.');
        }
    });

    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') btnLogin.click();
    });
});