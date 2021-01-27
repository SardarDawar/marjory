const expscrUpload = document.getElementById("exp_scr_upl");
const expscrButton = document.getElementById("exp_scr_btn");
const expscrReset = document.getElementById("exp_scr_rst");
const expscrFilename = document.getElementById("id_filename");
const expscrForm = document.getElementById("scriptsfile-form");
const respDownloadButton = document.getElementById("resp_down_btn");

const url_replica_exp_scr = "/api/replica/scriptsfile-upload";
const url_replica_images = "/api/replica/images-upload";
const url_replica_reset = "/api/replica/reset";
const url_responses_download = `api/replica/${replicaEntrypoint}/download-responses`;

download_responses = ()=>{
    const download_url = `/${url_responses_download}`;
    showLIModal_loader("Generating Responses File", replicaEntrypoint)
    var downloadWindow = window.open(download_url, '_blank');
    var stimer = setInterval(function() { 
        if(downloadWindow==null || downloadWindow.closed) {
            clearInterval(stimer);
            hideLIModal();
        }
    }, 500);
    setTimeout(()=> {
        clearInterval(stimer);
        hideLIModal();
    }, 30000);
}

window.onload = () => {
    hideLIModal();
}

if (document.readyState === "complete") {
    hideLIModal();
}

respDownloadButton.onclick = download_responses;

replica_experiment_scripts_upload = () => {    
    expscrUpload.click();
}

expscrUpload.onchange = function () {
    const fileName = expscrUpload.value.split('\\')[expscrUpload.value.split('\\').length - 1];
    if (!fileName || fileName.length===0) return;
    const fd = new FormData(expscrForm);
    fd.append("replica", replicaID);
    showLIModal_loader("Processing", fileName)
    
    ajax_upload_file(url_replica_exp_scr, fd, hsuccess_replica_exp_scripts, (xhr, status, error) => {
        showLIModal_info("Error!", "", `An unknown error has occured: ${error}`)
    });
};

ajax_upload_file = (_url, _data, hsuccess_extra, herror_extra) => {

    expscrUpload.value = ''
    imagesUpload.value = ''

    $.ajax({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }

            showLIModal_progress("Uploading", null, 0);
        }, 
        url: _url, 
        type: 'POST',
        data: _data,
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        enctype: 'multipart/form-data',
        xhr: function() {
            var xhr = new window.XMLHttpRequest();
            if(xhr.upload){
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        const fracComplete = evt.loaded / evt.total;
                        const percentComplete = Math.round(fracComplete * 100);
                        if (percentComplete >= 100) showLIModal_loader("Processing", null)
                        else updateLIModal_progress(null, null, percentComplete)
                    }
                    else {
                        showLIModal_loader("Uploading", null)
                    }
                }, false);
            }
            return xhr;
        },
        success: function(data){
            hsuccess_extra(data)
        },
        error: herror_extra,
        timeout: 600000 // set timeout to 10x60 seconds
    });
}

replica_reset = () => {
    
    expscrUpload.value = ''
    imagesUpload.value = ''

    showConfirmationModal("Replica Reset", "Are you sure about removing all scripts and images in this replica?", () => {
        
        showLIModal_loader("Resetting", "")

        $.ajax({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }, 
            url: url_replica_reset, 
            type: 'POST',
            data: {
                'replica': replicaID,
            },
            async: true,
            success: function(data){
                hsuccess_replica_exp_scripts(data)
            },
            error: function(error){
                showLIModal_info("Error!", "", "An unknown error has occured")
            },
            timeout: 60000 // set timeout to 1x60 seconds
        });

    })
}

hsuccess_replica_exp_scripts = (data) => {
    if ("error" in data)
    {
        if (data["error"])
        {
            // error has occurred, check if error has errorTitle, if so show specialInfo Modal
            if ("errorTitle" in data)
            {
                
                if ("message" in data)  showLIModal_infoSpecial(data["errorTitle"], data['message'])
                else                    showLIModal_infoSpecial(data["errorTitle"], "An unknown error has occured")
            }
            else 
            {                
                // an error has occured, no title
                if ("message" in data)  showLIModal_info("Error!", "", data['message'])
                else                    hideLIModal();
            }
        }
        else 
        {
            // success
            if ("message" in data)  showLIModal_info("Success", "", data['message'])
            else                    hideLIModal();
        }
        update_exp_scr_table(null);     // force call to server for updates
    }
    else hideLIModal();
}

expscrButton.onclick = replica_experiment_scripts_upload;
expscrReset.onclick = replica_reset;

// replica images

const imagesUpload = document.getElementById("images_upl");
const imagesButton = document.getElementById("images_btn");
const imagesForm = document.getElementById("images-form");
const imagesSelectButton = document.getElementById("imagesModal-btn-select");
const imagesUploadButton = document.getElementById("imagesModal-btn-upload");

imagesUploadButton.setAttribute("disabled", "true");

open_images_upload_modal = () => {
    imagesUploadButton.setAttribute("disabled", "true");
    showImagesModal(null, null, ()=>{
        imagesUpload.value = "";
        updateImagesModalFilelist(imagesUpload.files);
    });
};

imagesButton.onclick = open_images_upload_modal;

imagesSelectButton.onclick = () => {
    imagesUpload.click();
}

imagesUpload.onchange = () => {
    const fileList = imagesUpload.files; 
    if (fileList==null || fileList.length === 0) return;
    
    updateImagesModalFilelist(fileList);

    imagesUploadButton.removeAttribute("disabled");
}

imagesUploadButton.onclick =() => {
    const fileList = imagesUpload.files; 
    if (fileList==null || fileList.length === 0) return;
    const fd = new FormData(imagesForm);
    fd.append("replica", replicaID);
    hideImagesModal();
    showLIModal_loader("Uploading", "Replica Images")
    ajax_upload_file(url_replica_images, fd, hsuccess_replica_exp_scripts, (error) => {
        showLIModal_info("Error!", "", "An unknown error has occured")
    });
    
};

fetch_replace_exp_scr_table = () => {
    // fetch and update
    $('#table_exp_scr').load(document.URL +  ' #table_exp_scr', ()=> {
        document.getElementById("exp_scr_btn").onclick = replica_experiment_scripts_upload;
        document.getElementById("exp_scr_rst").onclick = replica_reset; 
        document.getElementById("images_btn").onclick = open_images_upload_modal;
        document.getElementById("resp_down_btn").onclick = download_responses;
    });
}

update_exp_scr_table = (data) => {
    expscrUpload.value = null;   
    imagesUpload.value = null;
    if (data === null)
    {
        fetch_replace_exp_scr_table();
    }
    else
    {
        // modify table field values
        // enable/diable table buttons
        // (fetch and replace works well enough -- but update could be done by DOM manipulation as well)
        fetch_replace_exp_scr_table();
    }
}


