const radioOpt1 = document.getElementById('radioTask_1')
const radioOpt2 = document.getElementById('radioTask_2')
const labelOpt1 = document.getElementById('custLabelTask_1')
const labelOpt2 = document.getElementById('custLabelTask_2')
const submitButton = document.getElementById('step-submit-btn')

const step_form = document.getElementById('id_step_form')
const form_input_response = document.getElementById('id_response')
const form_input_start = document.getElementById('id_start')
const form_input_finish = document.getElementById('id_finish')

const url_step_start = "/api/step/set-start";

submitButton.setAttribute('disabled', "true")
radioOpt2.checked = false
radioOpt1.checked = false

window.onload = (e) => {
    const now_milliseconds = Date.now()
    if (!form_input_start.value) form_input_start.value = now_milliseconds
    
    $.ajax({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }, 
        url: url_step_start, 
        type: 'POST',
        data: {
            'step_id': step_id,
            'step_start': now_milliseconds,
        },
        async: true,
        cache: false,
        success: function(data){
            // console.log(data['message'])
            // console.log(data['step_start'])
        },
        error: function(error){
            console.log(error);
        },
        timeout: 120000     // set timeout to 2x60 seconds
    });
}

$(document).on('click', '[data-toggle="lightbox"]', function(event) {
    event.preventDefault();
    $(this).ekkoLightbox();
});

labelOpt1.onclick = ()=>{
    radioOpt1.click()
}

labelOpt2.onclick = ()=>{
    radioOpt2.click()
}

radioOpt1.onclick = ()=> {
    if (!radioOpt1.checked) radioOpt1.checked = true
    if (radioOpt2.checked) radioOpt2.checked = false
    submitButton.removeAttribute('disabled')
}

radioOpt2.onclick = ()=> {
    if (!radioOpt2.checked) radioOpt2.checked = true
    if (radioOpt1.checked) radioOpt1.checked = false
    submitButton.removeAttribute('disabled')
}

submitButton.onclick = (e) => {
    if (radioOpt1.checked && radioOpt2.checked)
    {
        submitButton.setAttribute('disabled', "true")
        radioOpt2.checked = false
        radioOpt1.checked = false
        return;
    }
    
    if (radioOpt1.checked) form_input_response.value = 1
    else if (radioOpt2.checked) form_input_response.value = 2
    else 
    {
        submitButton.setAttribute('disabled', "true")
        return;
    }
    
    form_input_finish.value = Date.now()
    step_form.submit();
}

setTimeout(()=>{
    console.log("session time ended")
    
    if (!(radioOpt1.checked && radioOpt2.checked))
    {
        if (radioOpt1.checked) 
        {
            form_input_response.value = 1
            form_input_finish.value = Date.now()
        }
        else if (radioOpt2.checked) 
        {
            form_input_response.value = 2
            form_input_finish.value = Date.now()
        }
    }

    step_form.submit();
    
}, Math.round(remaining_seconds*1000))

const timerClock = document.getElementById('id_clock_icon')
const timerText = document.getElementById('id_time_text')
const timerMinutes = document.getElementById('id_rem_time_mins')
const TIMER_UPDATE_INTERVAL = 60;       // 60 seconds
var current_remaining_seconds = remaining_seconds;

getTimerMinutes = () => {
    return Math.round(current_remaining_seconds/60)
}

timerMinutes.innerHTML = `${getTimerMinutes()}`;

updateTimerMinsText = () => {
    current_remaining_seconds -= TIMER_UPDATE_INTERVAL;            // remove a minute
    timerMinutes.innerHTML = `${getTimerMinutes()}`;
    setTimeout(updateTimerMinsText, 1000*TIMER_UPDATE_INTERVAL)    // run every minute
}

setTimeout(updateTimerMinsText, 1000*TIMER_UPDATE_INTERVAL);       // start after 1 minute

toggleTimer = () => {
    if ($('#id_time_text').is(":visible"))  hideTimer();
    else showTimer();
}

hideTimer = () => {
    $('#id_time_text').fadeOut(100);
    // if ($('#id_clock_icon').hasClass('text-primary')) $('#id_clock_icon').removeClass('text-primary')
    if ($('#id_clock_icon').hasClass('shadow')) $('#id_clock_icon').removeClass('shadow')
}

showTimer = () => {
    $('#id_time_text').fadeIn(100);
    // if (!$('#id_clock_icon').hasClass('text-primary')) $('#id_clock_icon').addClass('text-primary')
    if (!$('#id_clock_icon').hasClass('shadow')) $('#id_clock_icon').addClass('shadow')
}

timerClock.onclick = toggleTimer;