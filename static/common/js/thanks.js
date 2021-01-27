const emailInput = document.getElementById('id_email');
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