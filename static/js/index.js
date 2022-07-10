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
                document.getElementById("error-message").innerHTML = "Houve um erro ao processar sua solicitação, verifique se o link digitado é valido."
                toast.show()
                setDefault()
                return false
            }
            checkDownloadIsDone(result.filename)
        }).catch(() => {
            let toastElement = document.getElementById('toast-error')
            let toast = bootstrap.Toast.getOrCreateInstance(toastElement)
            document.getElementById("error-message").innerHTML = "Desculpe, o tempo de resposta do servidor excedeu o esperado."
            toast.show()
            setDefault()
            return false
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

function checkDownloadIsDone(file) {
    let check = setInterval(() => {
        fetch(`/done?filename=${file}`, {
            method: 'GET',
            headers: {"Content-type": "application/json"}
        }).then(response => response.json())
        .then((result) => {
            if(result.link != false) {
                let button_convert = document.getElementById("btn-convert")
                button_convert.innerHTML = 'Clique aqui para baixar seu arquivo'
                button_convert.classList.remove('btn-primary')
                button_convert.classList.add('btn-success')
                button_convert.setAttribute('href', result.link)
                button_convert.setAttribute('onclick', 'setDefault()')
                clearInterval(check)
            }
        })
    }, 2000);
}