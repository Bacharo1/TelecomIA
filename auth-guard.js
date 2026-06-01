// auth-guard.js
(async function() {
    try {
        const res = await fetch('http://localhost:8001/api/me', {
            credentials: 'include'
        });
        if (!res.ok) {
            window.location.replace('login.html');
            return;
        }
        //  Session valide on affiche la page
        document.body.style.visibility = 'visible';
    } catch {
        window.location.replace('login.html');
    }
})();