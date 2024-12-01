const homeButton = document.querySelector('.buttonHome')

function changePage(){
    window.location.href = '/'
}

homeButton.addEventListener('click', () => window.location.href = '/')

