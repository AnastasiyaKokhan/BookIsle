document.querySelectorAll('.filter__genre-list-parent-input').forEach(element => {
        element.addEventListener('change', function() {
            let isChecked = this.checked;
            let childInputs = this.parentElement.nextElementSibling.querySelectorAll('.filter__genre-list-children-child-input');
            if (childInputs.length > 0) {
                childInputs.forEach(childInput => {
                    childInput.checked = isChecked;
                });
            }
        });
    });

document.querySelectorAll('.filter__genre-list-children-child-input').forEach(childInput => {
    childInput.addEventListener('change', function() {
        let parentInput = this.closest('.filter__genre-list').querySelector('.filter__genre-list-parent-input');
        let childInputs = this.closest('.filter__genre-list-children').querySelectorAll('.filter__genre-list-children-child-input');
        let anyChecked = Array.from(childInputs).some(input => input.checked);
        parentInput.checked = anyChecked;
    });
});
