
const API_URL = "http://localhost:8001";

const pwdInput      = document.getElementById('password');
const confInput     = document.getElementById('confirmPassword');
const bars          = [document.getElementById('bar1'), document.getElementById('bar2'), document.getElementById('bar3')];
const strengthLabel = document.getElementById('strengthLabel');
const matchEl       = document.getElementById('matchIndicator');
const equipeInput   = document.getElementById('equipeId');
const levels        = ['Faible', 'Moyen', 'Fort'];
const classes       = ['weak', 'medium', 'strong'];

// --- Force du mot de passe ---
pwdInput.addEventListener('input', () => {
    const v = pwdInput.value;
    let score = 0;
    if (v.length >= 6) score++;
    if (/[A-Z]/.test(v) && /[0-9]/.test(v)) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;
    bars.forEach((b, i) => {
        b.className = 'strength-bar';
        if (i < score) b.classList.add(classes[score - 1]);
    });
    strengthLabel.textContent = v.length === 0 ? 'Force du mot de passe' : (levels[score - 1] || 'Faible');
    checkMatch();
});

confInput.addEventListener('input', checkMatch);

function checkMatch() {
    if (!confInput.value) { matchEl.textContent = ''; return; }
    if (pwdInput.value === confInput.value) {
        matchEl.className = 'match-ok';
        matchEl.textContent = '✓ Les mots de passe correspondent';
    } else {
        matchEl.className = 'match-fail';
        matchEl.textContent = '✗ Les mots de passe ne correspondent pas';
    }
}

// --- Soumission ---
document.getElementById('btnRegister').addEventListener('click', async () => {
    const username   = document.getElementById('username').value.trim();
    const password   = pwdInput.value;
    const confirm    = confInput.value;
    const errorMsg   = document.getElementById('errorMsg');
    const successMsg = document.getElementById('successMsg');
    const btn        = document.getElementById('btnRegister');
    const equipeId   = equipeInput.value.trim();

    errorMsg.className   = 'error-msg';
    successMsg.className = 'success-msg';

    // Validation
    if (!username) {
        errorMsg.textContent = 'Veuillez entrer un identifiant.';
        errorMsg.className = 'error-msg visible'; return;
    }
    if (!/^[a-zA-Z0-9_.-]{3,}$/.test(username)) {
        errorMsg.textContent = 'Identifiant invalide (min. 3 car., lettres/chiffres/_ . -).';
        errorMsg.className = 'error-msg visible'; return;
    }
    if (password.length < 6) {
        errorMsg.textContent = 'Mot de passe trop court (min. 6 caractères).';
        errorMsg.className = 'error-msg visible'; return;
    }
    if (password !== confirm) {
        errorMsg.textContent = 'Les mots de passe ne correspondent pas.';
        errorMsg.className = 'error-msg visible'; return;
    }
    if (!equipeInput.value) {
        errorMsg.textContent = "Veuillez sélectionner une équipe.";
        errorMsg.className = 'error-msg visible'; return;
    }

    // Appel API
    btn.disabled = true;
    btn.textContent = "Création en cours...";

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username:  username,
                password:  password,
                equipe_id:  equipeId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            errorMsg.textContent = data.detail || "Erreur lors de la création du compte.";
            errorMsg.className = 'error-msg visible';
            btn.disabled = false;
            btn.textContent = "Créer mon compte";
            return;
        }

        // Succès
        successMsg.className = 'success-msg visible';
        setTimeout(() => { window.location.href = 'login.html'; }, 2200);

    } catch (err) {
        errorMsg.textContent = "Impossible de contacter le serveur.";
        errorMsg.className = 'error-msg visible';
        btn.disabled = false;
        btn.textContent = "Créer mon compte";
    }
});