const entrypoint_link_input = document.getElementById("entrypoint_link") 

run_script = () => {
    const entrypoint_link = entrypoint_link_input.value;

    if (entrypoint_link !== null && entrypoint_link.length !== 0)
    {
        window.location.href=`/s/load?epl=${entrypoint_link}`;
    }
}

entrypoint_link_input.addEventListener("keyup", function(event) {
    if (event.key === 'Enter') {
        run_script()
    }
});