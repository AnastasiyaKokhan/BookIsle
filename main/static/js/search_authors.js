const searchInput = document.getElementById('search_authors');
    searchInput.addEventListener('input', getSearchResult);

const searchResult = document.querySelector('.author_list');

function getSearchResult() {
    if (searchInput.value.length > 2) {
        fetch(`http://127.0.0.1:8000/api/search_authors/?search_authors=${searchInput.value}`)
            .then(resp => resp.json())
            .then((data) => {
                searchResult.style.display = 'block';
                searchResult.innerHTML = '';
                for (let item of data) {
                    searchResult.innerHTML += `
                    <div class="author">
                        <input type="checkbox" name="author_choice" value="${item.id}" id="author_${item.id}" class="author_input">
                        <label for="author_${item.id}">${item.first_name} ${item.last_name}</label>
                    </div>
                    `;
                }
                if (data.length === 0) {
                    searchResult.innerHTML = `
                    <div class="not_found">
                        <p>По вашему запросу ничего не найдено</p>
                    </div>
                    `;
                }
            });
    } else {
        searchResult.style.display = 'none';
        searchResult.innerHTML = '';
    }
}
