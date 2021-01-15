const searchButton = document.getElementById('search-btn');
const searchInput = document.getElementById('search-input');

searchButton.onclick = e => {
    // yes, I could use "required" but it's ugly
    if (searchInput.value.length == 0) {    
        e.preventDefault();
    }
};