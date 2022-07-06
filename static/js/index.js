function convert() {
    let link = document.getElementById("link").value
    let button_convert = document.getElementById("btn-convert")

    if(!link.trim() || link.length === 0) {
        document.getElementById("link").classList.add('border-danger')
        return false
    }
    document.getElementById("link").classList.remove('border-danger')

    fetch(`/convert?link=${link}`, {
        method: 'POST',
        headers: {"Content-type": "application/json"}
    })
        .then(response => response.json())
        .then(result => {
            if(result.erro != null) {
                let toastElement = document.getElementById('toast-error')
                let toast = bootstrap.Toast.getOrCreateInstance(toastElement)
                toast.show()
                setDefault()
                return false
            }
            button_convert.innerHTML = 'Clique aqui para baixar seu arquivo'
            button_convert.classList.remove('btn-primary')
            button_convert.classList.add('btn-success')
            button_convert.setAttribute('href', result.link)
            button_convert.setAttribute('onclick', 'setDefault()')
            return true
        })

    button_convert.disabled = true
    button_convert.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Processando...
    `
}

function setDefault() {
    setTimeout(() => {
        let button_convert = document.getElementById("btn-convert")
        button_convert.innerHTML = 'Converter'
        button_convert.classList.remove('btn-success')
        button_convert.classList.add('btn-primary')
        button_convert.removeAttribute('href')
        button_convert.setAttribute('onclick', 'convert()')
        document.getElementById("link").value = ''
    }, 1000)
}