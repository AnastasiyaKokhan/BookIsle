document.querySelectorAll('.filter__genre-list-parent-input').forEach(function(element) {
        element.addEventListener('change', function() {
            var isChecked = this.checked;
            var childInputs = this.parentElement.nextElementSibling.querySelectorAll('.filter__genre-list-children-child-input');

            if (childInputs.length > 0) {
                childInputs.forEach(function(childInput) {
                    childInput.checked = isChecked;
                });
            }
        });
    });
