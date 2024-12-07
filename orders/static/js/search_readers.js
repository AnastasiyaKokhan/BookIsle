const searchInput = document.getElementById('search_readers');
    searchInput.addEventListener('input', getSearchResult);

const searchResult = document.querySelector('.readers_list');

function getSearchResult() {
    if (searchInput.value.length > 2) {
        fetch(`http://127.0.0.1:8000/api/search_readers/?search_readers=${searchInput.value}`)
            .then(resp => resp.json())
            .then((data) => {
                searchResult.style.display = 'block';
                searchResult.innerHTML = '';
                for (let item of data) {
                    searchResult.innerHTML += `
                    <div class="reader">
                        <input type="radio" name="reader" value="${item.id}" id="reader_${item.id}">
                        <label for="reader_${item.id}">${item.first_name} ${item.last_name}</label>
                    </div>
                    `;
                }
                if (data.length === 0) {
                    searchResult.innerHTML = `
                    <div class="not_found">
                        <p>по вашему запросу ничего не найдено</p>
                    </div>
                    `;
                }
            });
    } else {
        searchResult.style.display = 'none';
        searchResult.innerHTML = '';
    }
}
