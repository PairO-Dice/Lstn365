const aboutButton = document.querySelector('.buttonAbout')

function changePage(){
    window.location.href = './about.html'
}

aboutButton.addEventListener('click', () => window.location.href = '../Pages/about.html')

