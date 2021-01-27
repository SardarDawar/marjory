// ####################################
//
// csrf cookie
//
// ####################################

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

var headers = new Headers();
headers.append('X-CSRFToken', csrftoken);

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


// ####################################
//
// modals api
//
// ####################################

var loadingInfoModalCloseAction = null;
var imagesModalCloseAction = null;
var imagesModalCloseCallback = null;

function showLIModal_loader(title, subtext) {
    $('body').css('overflow', 'hidden');

    if (title!==null) $('#loadingInfoModalTitle').html(title)
    if (subtext!==null) $('#loadingInfoModalTitleSecondary').html(subtext)
    $('#loadingInfoModalTitleSpecial').html("").hide()

    $('#loadingInfoModalContent-text').html("").hide()
    $('#loadingInfoModalContent-progress').hide()
    $('#loadingInfoModalContent-loader').show();

    $('#loadingInfoModalHeader-close').hide();
    $('#loadingInfoModal-footer').hide();

    $('#loadingInfoModal').modal('show')
}

function showLIModal_info(title, subtext, content, closeAction) {
    $('body').css('overflow', 'hidden');

    if (title!==null) $('#loadingInfoModalTitle').html(title)
    if (subtext!==null) $('#loadingInfoModalTitleSecondary').html(subtext)
    $('#loadingInfoModalTitleSpecial').html("").hide()

    $('#loadingInfoModalContent-loader').hide()
    $('#loadingInfoModalContent-progress').hide()
    if (content!==null) $('#loadingInfoModalContent-text').html(content).show();

    $('#loadingInfoModalHeader-close').show();
    $('#loadingInfoModal-footer').show();

    loadingInfoModalCloseAction = closeAction;

    $('#loadingInfoModal').modal('show')
    $('#loadingInfoModal').modal('handleUpdate')
}

function showLIModal_progress(title, subtext, initialValue) {
    $('body').css('overflow', 'hidden');

    if (title!==null) $('#loadingInfoModalTitle').html(title)
    if (subtext!==null) $('#loadingInfoModalTitleSecondary').html(subtext)
    $('#loadingInfoModalTitleSpecial').html("").hide()

    $('#loadingInfoModalContent-text').html("").hide()
    $('#loadingInfoModalContent-loader').hide();
    $('#loadingInfoModalContent-progress').show()
    
    $('#loadingInfoModalHeader-close').hide();
    $('#loadingInfoModal-footer').hide();
    
    updateLIModal_progress(null, null, initialValue);

    $('#loadingInfoModal').modal('show')
}

function updateLIModal_progress(title, subtext, newValue) {
    if (title!==null) $('#loadingInfoModalTitle').html(title)
    if (subtext!==null) $('#loadingInfoModalTitleSecondary').html(subtext)
    $('#loadingInfoModalTitleSpecial').html("").hide()
    if (newValue === null || newValue <= 0)
    {
        $('#loadingInfoModalContent-progress > .progress > .progress-bar').css('width', '0%')
        $('#loadingInfoModalContent-progress > .progress > .progress-bar').html('')
    }
    else
    {
        $('#loadingInfoModalContent-progress > .progress > .progress-bar').css('width', `${newValue}%`)
        $('#loadingInfoModalContent-progress > .progress > .progress-bar').html(`${newValue}%`)
    }
}

function hideLIModal() {
    $('#loadingInfoModal').modal('hide')
    if ($('#loadingInfoModal').hasClass('show'))
    {
        setTimeout(hideLIModal, 250)
    }
}

$('#loadingInfoModal').on('hidden.bs.modal', function(){
    // enable only if other modals are not visible
    if(!($('#loadingInfoModal').hasClass('show') || $('#imagesModal').hasClass('show') || $('#confirmationModal').hasClass('show')))
    {
        $('body').css('overflow', 'auto');
    }
    $('#loadingInfoModalTitle').html('')
    $('#loadingInfoModalTitleSecondary').html('')
    $('#loadingInfoModalTitleSpecial').html("").hide()
    $('#loadingInfoModalContent-loader').hide()
    $('#loadingInfoModalContent-text').html('').hide()
    $('#loadingInfoModalContent-progress').hide()
    $('#loadingInfoModalContent-progress > .progress > .progress-bar').css('width', '0%')
    $('#loadingInfoModalContent-progress > .progress > .progress-bar').html('')
    $('#loadingInfoModalContent-progress').hide()
    $('#loadingInfoModalHeader-close').hide();
    $('#loadingInfoModal-footer').hide();
}).on('shown.bs.modal', function(){
    $('body').css('overflow', 'hidden');
})

$('#loadingInfoModal').on('hide.bs.modal', function(){
    if (loadingInfoModalCloseAction) loadingInfoModalCloseAction();
    loadingInfoModalCloseAction = null;
})

function showLIModal_infoSpecial(special, content, closeAction) {
    $('body').css('overflow', 'hidden');

    $('#loadingInfoModalTitle').html("")
    $('#loadingInfoModalTitleSecondary').html("")
    $('#loadingInfoModalTitleSpecial').html(special).show()

    $('#loadingInfoModalContent-loader').hide()
    $('#loadingInfoModalContent-progress').hide()
    if (content!==null) $('#loadingInfoModalContent-text').html(content).show();

    $('#loadingInfoModalHeader-close').show();
    $('#loadingInfoModal-footer').show();

    loadingInfoModalCloseAction = closeAction;

    $('#loadingInfoModal').modal('show')
    $('#loadingInfoModal').modal('handleUpdate')
}

function showImagesModal(title, subtext, closeAction) {
    $('body').css('overflow', 'hidden');

    if (title!==null) $('#imagesModalTitle').html(title)
    if (subtext!==null) $('#imagesModalTitleSecondary').html(subtext)

    imagesModalCloseAction = closeAction;

    $('#imagesModal').modal('show')
}

function updateImagesModalFilelist(fileList) {
    if (fileList===null || fileList.length===0)
    {
        $('#images-filetable').hide();
        $('#images-content-text').show();
    }
    else
    {
        $('#images-filetable-body').html("")
        for(var i=0; i<fileList.length; i++)
        {
            $('#images-filetable-body').append(`
            <tr>
                <th scope="row">${i+1}</th>
                <td>${fileList[i].name}</td>
                <td>${fileList[i].type}</td>
                <td>${(fileList[i].size/1024).toFixed(1)}</td>
            </tr>
            `)
        }
        $('#images-content-text').hide();
        $('#images-filetable').show();
    }
}

function hideImagesModal(callback) {
    $('#imagesModal').modal('hide')
    if (callback !== null) imagesModalCloseCallback = callback;
}

$('#imagesModal').on('hidden.bs.modal', function(){
    // enable only if other modals are not visible
    if(!($('#loadingInfoModal').hasClass('show') || $('#imagesModal').hasClass('show') || $('#confirmationModal').hasClass('show')))
    {
        $('body').css('overflow', 'auto');
    }
    if (imagesModalCloseAction) imagesModalCloseAction();
    imagesModalCloseAction = null;
    if (imagesModalCloseCallback) imagesModalCloseCallback();
    imagesModalCloseCallback = null;
}).on('shown.bs.modal', function(){
    $('body').css('overflow', 'hidden');
})

function showConfirmationModal(title, content, confirmAction) {
    if (title!==null) $('#confirmationModalTitle').html(title)
    $('#confirmationModalContent').html(content)
    $('#confirmationModalConfirm').on('click.confirmAction', () => {
        $('#confirmationModal').modal('hide');
        confirmAction();
    })
    $('#confirmationModal').modal('show')
}

function showConfirmationModalCustom(title, content, customText, confirmAction) {
    $('#confirmationModalConfirm').html(customText)
    showConfirmationModal(title, content, confirmAction)
}

$('#confirmationModal').on('hidden.bs.modal', function (e) {
    // enable only if other modals are not visible
    if(!($('#loadingInfoModal').hasClass('show') || $('#imagesModal').hasClass('show') || $('#confirmationModal').hasClass('show')))
    {
        $('body').css('overflow', 'auto');
    }
    $('#confirmationModalConfirm').html("Yes, I'm sure")
    $('#confirmationModalConfirm').off('click.confirmAction')
    $('#confirmationModalTitle').html('Confirmation')
    $('#confirmationModalContent').html('...')
})

$('#confirmationModal').on('show.bs.modal', function(){
    $('body').css('overflow', 'hidden');
})
