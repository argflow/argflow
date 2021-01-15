const loginTabBtn = document.getElementById('login-tab-btn');
const registerTabBtn = document.getElementById('register-tab-btn');

const loginTabLi = document.getElementById('login-tab-li');
const registerTabLi = document.getElementById('register-tab-li');

const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');

loginTabBtn.onclick = e => {
    e.preventDefault();
    loginTabLi.classList.add('is-active');
    registerTabLi.classList.remove('is-active');
    registerTab.classList.add('hidden');
    loginTab.classList.remove('hidden');
}

registerTabBtn.onclick = e => {
    e.preventDefault();
    loginTabLi.classList.remove('is-active');
    registerTabLi.classList.add('is-active');
    registerTab.classList.remove('hidden');
    loginTab.classList.add('hidden');
}