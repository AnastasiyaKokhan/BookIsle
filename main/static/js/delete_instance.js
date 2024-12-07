function deleteBookInstance(event) {
   if (confirm('Вы действительно хотите удалить данный экземпляр книги?')) {
       document.getElementById('delete_book_instance_button').submit();
   } else {
       event.preventDefault();
       return false;
   }
}
