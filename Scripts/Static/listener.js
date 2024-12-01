const aboutButton = document.querySelector('.buttonAbout')

function changePage(){
    window.location.href = '/about'
}

aboutButton.addEventListener('click', () => window.location.href = '/about')

