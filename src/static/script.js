const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
const showPassword1 = document.getElementById('togglePassword-sembunyi')
const showPassword2 = document.getElementById('togglePassword-muncul')
const pw = document.getElementById('password1')

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

function showPassword() {
    showPassword1.setAttribute("hidden",true)
    showPassword2.removeAttribute("hidden")
    pw.removeAttribute("type")
}

function hidePassword() {
    showPassword2.setAttribute("hidden",true)
    showPassword1.removeAttribute("hidden")
    pw.setAttribute("type","password")
}
