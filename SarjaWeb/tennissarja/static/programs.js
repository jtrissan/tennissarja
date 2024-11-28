

function validateEmail (email) {
    return /^[^@]+@[^@]+\.[a-z]{2,}$/i.test(email);
}
function validatePassword (password) {
    return password.length >= 8;
}
function validatePhone (phone) {
    return /^\+?\d{10,15}$/.test(phone);
}

function validateRegForm() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const phone = document.getElementById('phone').value;

    if (!validateEmail(email)) {
        document.getElementById('emailError').textContent = 'Virheellinen sähköpostiosoite.';
        valid = false;
    } else {
        document.getElementById('emailError').textContent = '';
    }

    if (!validatePassword(password)) {
        document.getElementById('passwordError').textContent = 'Salasanan pitää olla vähintään 8 merkkiä pitkä.';
        valid = false;
    } else {
        document.getElementById('passwordError').textContent = '';
    }

    if (!validatePhone(phone)) {
        document.getElementById('phoneError').textContent = 'Virheellinen puhelinnumero.';
        valid = false;
    } else {
        document.getElementById('phoneError').textContent = '';
    }
}

/*document.getElementById('regForm').addEventListener('submit', function (event) {
    event.preventDefault();
    validateRegForm();
    });
    */
