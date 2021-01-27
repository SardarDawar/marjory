const emailInput = document.getElementById('id_participant');
const contactCheck = document.getElementById('id_contactme');

function validEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
};

emailInput.onchange = () => {
    if (validEmail(emailInput.value)) contactCheck.removeAttribute('disabled')
    else 
    {
        contactCheck.setAttribute('disabled', true)
        contactCheck.checked = false
    }
}

emailInput.onfocus = () => {
    if (validEmail(emailInput.value)) contactCheck.removeAttribute('disabled')
    else 
    {
        contactCheck.setAttribute('disabled', true)
        contactCheck.checked = false
    }
}

emailInput.onkeyup = () => {
    if (validEmail(emailInput.value)) contactCheck.removeAttribute('disabled')
    else 
    {
        contactCheck.setAttribute('disabled', true)
        contactCheck.checked = false
    }
}

if (validEmail(emailInput.value)) contactCheck.removeAttribute('disabled')
else 
{
    contactCheck.setAttribute('disabled', true)
    contactCheck.checked = false
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

const copyClipboard = document.getElementById('id_copy_clip');
const keyParticipation = document.getElementById('id_key_particip');

const copyToClipboard = str => {
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
};


copyClipboard.onclick = () => {
    copyToClipboard(keyParticipation.value)
}
