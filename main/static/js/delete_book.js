function deleteBook(event) {
   if (confirm('Вы действительно хотите удалить книгу? Вся информация о книге и ее экземпляры будут удалены')) {
       document.getElementById('delete_book_button').submit();
   } else {
       event.preventDefault();
       return false;
   }
}
