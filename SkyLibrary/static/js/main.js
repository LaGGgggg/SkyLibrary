const top_panel = document.querySelector('.navbar');

if (top_panel !== null) {
    topPanelShowHandler(top_panel);
}

function topPanelShowHandler(top_panel) {

    const top_panel_ul_tag = top_panel.querySelector('ul');

    if (top_panel_ul_tag.childNodes.length == 0) {
        top_panel.style.display = 'none';
    }
}
