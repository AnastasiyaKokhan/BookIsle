let count = 0;

function createAuthorInputs() {
    if (count < 9) {
        count++;

        let container = document.createElement('div');
        container.classList.add('added_author');
        container.innerHTML = `
            <div class="new_author_inputs">
                <input type="text" name="new_author_last_name_${count}" placeholder="Фамилия*">
                <input type="text" name="new_author_first_name_${count}" placeholder="Имя">
                <input type="text" name="new_author_patronymic_${count}" placeholder="Отчество">
            </div>
            <div class="new_author_photos">
                <input type="file" accept="image/*" name="new_author_photos_${count}">
                <input type="file" accept="image/*" name="new_author_photos_${count}">
            </div>
        `;
        document.querySelector('.added_author_inputs').append(container);
    }
}

document.querySelector('.plus').addEventListener('click', createAuthorInputs);
