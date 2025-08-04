(function(){
    const btnEliminacion = document.querySelectorAll(".btnEliminacion");

    btnEliminacion.forEach(btn => {
        btn.addEventListener('click',(e) => {
            const confirmacion = confirm('¿Seguro que desea borrar?');
            if (!confirmacion){
                e.preventDefault();
            }
        });
    });
})();