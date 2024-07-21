function clicked(event) {
   if (confirm('Вы действительно хотите удалить книгу?')) {
       document.getElementById('.delete_button').submit();
   } else {
       event.preventDefault();
       return false;
   }
}
