let count = 0;

function createAuthorInputs() {
    if (count < 9) {
        count++;

        let container = document.createElement('div');
        container.classList.add('added_author');
        container.innerHTML = `
            <div class="author_inputs">
                <input type="text" name="last_name_${count}" placeholder="Фамилия*">
                <input type="text" name="first_name_${count}" placeholder="Имя*">
                <input type="text" name="patronymic_${count}" placeholder="Отчество">
            </div>
            <div class="author_photos">
                <input type="file" accept="image/*" name="photos_${count}">
                <input type="file" accept="image/*" name="photos_${count}">
            </div>
        `;
        document.querySelector('.added_author_inputs').append(container);
    }
}

document.querySelector('.plus').addEventListener('click', createAuthorInputs);
