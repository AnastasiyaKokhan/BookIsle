const aboutImg = document.querySelector('.description__image > img')
const aboutListImg = document.querySelectorAll('.description__image-list-item > img')

aboutListImg.forEach(item => {
    item.addEventListener('click', () => {
        console.log();
        for(let i of item.parentNode.parentNode.children){
            if(i.classList.contains('description__image-list-item-active')){
                i.classList.remove('description__image-list-item-active')
            }
        }
        item.parentElement.classList.add('description__image-list-item-active')
        aboutImg.setAttribute('src', item.getAttribute('src'))
    })
})
